"""
POST /api/chat — streaming RAG chat endpoint.

Returns Server-Sent Events:
  - {"type": "citations", "data": [...]}
  - {"type": "token", "data": "Hello"}
  - {"type": "session_id", "data": "uuid"}
  - {"type": "done", "data": ""}
  - {"type": "error", "data": "message"}
"""

import json
from typing import AsyncGenerator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.schemas import ChatRequest
from app.services import (
    build_messages,
    ensure_session,
    save_chat_messages,
    stream_chat_response,
)

router = APIRouter(prefix="/api", tags=["chat"])


async def generate_sse(
    req: ChatRequest, db_session: AsyncSession
) -> AsyncGenerator[str, None]:
    """Main SSE generator: embed, retrieve, build context, stream LLM."""
    client = AsyncOpenAI(
        api_key=settings.openai_api_key, base_url=settings.openai_base_url
    )

    try:
        # Ensure session exists
        session_id = await ensure_session(db_session, req.session_id)
        yield f"data: {json.dumps({'type': 'session_id', 'data': session_id})}\n\n"

        # Build messages with RAG context
        messages, citations = await build_messages(
            db_session, req.message, session_id, req.url, client
        )

        # Send citations first
        yield f"data: {json.dumps({'type': 'citations', 'data': citations})}\n\n"

        # Stream tokens and capture full response
        full_response = ""
        async for sse_line in stream_chat_response(messages, client):
            if '"type": "token"' in sse_line:
                data = json.loads(sse_line.removeprefix("data: "))
                full_response += data["data"]
            yield sse_line

        # Save to DB after streaming
        await save_chat_messages(
            db_session, session_id, req.message, full_response, citations
        )

    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'data': str(e)})}\n\n"


@router.post("/chat")
async def chat(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    return StreamingResponse(
        generate_sse(req, db),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
