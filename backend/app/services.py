import json
import uuid
from typing import AsyncGenerator

from openai import AsyncOpenAI
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import ChatMessage, ChatSession, Document


async def retrieve_documents(
    session: AsyncSession,
    query_embedding: list[float],
    filter_url: str | None = None,
    top_k: int | None = None,
) -> list[dict]:
    """Hybrid vector search with optional URL filter using cosine similarity."""
    if top_k is None:
        top_k = settings.top_k

    query = select(
        Document.content,
        Document.metadata_,
        Document.embedding.cosine_distance(query_embedding).label("distance"),
    ).order_by(Document.embedding.cosine_distance(query_embedding))

    if filter_url:
        query = query.where(Document.metadata_["url"].astext == filter_url)

    query = query.limit(top_k)
    result = await session.execute(query)
    rows = result.all()

    return [
        {
            "content": row.content,
            "metadata": row.metadata_,
            "distance": float(row.distance),
        }
        for row in rows
    ]


async def get_chat_history(
    session: AsyncSession, session_id: str, limit: int | None = None
) -> list[dict]:
    """Fetch recent chat messages for a session."""
    if limit is None:
        limit = settings.max_history_messages

    query = (
        select(ChatMessage.role, ChatMessage.content)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
    )
    result = await session.execute(query)
    rows = result.all()

    # Return in chronological order
    return [{"role": row.role, "content": row.content} for row in reversed(rows)]


async def save_chat_messages(
    session: AsyncSession,
    session_id: str,
    user_message: str,
    assistant_message: str,
    citations: list[dict] | None = None,
) -> None:
    """Persist user and assistant messages after streaming completes."""
    now_utc = __import__("datetime").datetime.utcnow()

    user_msg = ChatMessage(
        id=uuid.uuid4(),
        session_id=session_id,
        role="user",
        content=user_message,
        created_at=now_utc,
    )
    assistant_msg = ChatMessage(
        id=uuid.uuid4(),
        session_id=session_id,
        role="assistant",
        content=assistant_message,
        citations=citations,
        created_at=now_utc,
    )
    session.add_all([user_msg, assistant_msg])

    # Update session title with first message if still default
    chat_session = await session.get(ChatSession, session_id)
    if chat_session and chat_session.title == "New Chat":
        chat_session.title = user_message[:50]

    await session.commit()


async def ensure_session(session: AsyncSession, session_id: str | None) -> str:
    """Create a new session if none provided, otherwise verify existing."""
    if session_id:
        existing = await session.get(ChatSession, session_id)
        if existing:
            return session_id

    new_session = ChatSession(id=uuid.uuid4())
    session.add(new_session)
    await session.commit()
    return str(new_session.id)


async def build_messages(
    session: AsyncSession,
    user_message: str,
    session_id: str,
    filter_url: str | None,
    client: AsyncOpenAI,
) -> tuple[list[dict], list[dict]]:
    """Build the messages array for the LLM, including RAG context and history."""
    # 1. Embed user question
    embedding_resp = await client.embeddings.create(
        model=settings.embedding_model,
        input=[user_message],
        dimensions=settings.embedding_dimensions,
    )
    query_embedding = embedding_resp.data[0].embedding

    # 2. Retrieve relevant documents
    docs = await retrieve_documents(session, query_embedding, filter_url)

    citations = [
        {
            "url": d["metadata"].get("url", d["metadata"].get("source", "")),
            "title": d["metadata"].get("title", ""),
            "content": d["content"][:200],
        }
        for d in docs
    ]

    # 3. Get chat history
    history = await get_chat_history(session, session_id)

    # 4. Build context from retrieved docs
    context_parts = []
    for i, d in enumerate(docs):
        source = d["metadata"].get("title", d["metadata"].get("source", f"Doc {i+1}"))
        context_parts.append(f"[Source {i+1}: {source}]\n{d['content']}")
    context_text = "\n\n".join(context_parts)

    # 5. Build messages array
    system_prompt = (
        "You are a helpful documentation assistant. Use the provided context "
        "to answer the user's question. If the context doesn't contain the answer, "
        "say so honestly. Always cite your sources by referring to the [Source N] "
        "labels in your response."
    )

    messages: list[dict] = [{"role": "system", "content": system_prompt}]

    # Insert history (already chronologically ordered from get_chat_history)
    messages.extend(history)

    # Insert current question with RAG context
    user_with_context = (
        f"Context from documentation:\n\n{context_text}\n\n"
        f"User question: {user_message}"
    )
    messages.append({"role": "user", "content": user_with_context})

    return messages, citations


async def stream_chat_response(
    messages: list[dict], client: AsyncOpenAI
) -> AsyncGenerator[str, None]:
    """Stream LLM response as SSE data lines."""
    stream = await client.chat.completions.create(
        model=settings.chat_model,
        messages=messages,
        stream=True,
    )

    async for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            token = chunk.choices[0].delta.content
            yield f"data: {json.dumps({'type': 'token', 'data': token})}\n\n"

    yield f"data: {json.dumps({'type': 'done', 'data': ''})}\n\n"
