"""
Session and message management endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import ChatMessage, ChatSession
from app.schemas import ChatMessageResponse, ChatSessionResponse, SessionCreate

router = APIRouter(prefix="/api", tags=["sessions"])


@router.post("/sessions", response_model=ChatSessionResponse)
async def create_session(
    body: SessionCreate, db: AsyncSession = Depends(get_db)
) -> ChatSession:
    session = ChatSession(title=body.title)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


@router.get("/sessions", response_model=list[ChatSessionResponse])
async def list_sessions(db: AsyncSession = Depends(get_db)) -> list[ChatSession]:
    result = await db.execute(
        select(ChatSession).order_by(ChatSession.updated_at.desc()).limit(50)
    )
    return list(result.scalars().all())


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_session(
    session_id: str, db: AsyncSession = Depends(get_db)
) -> ChatSession | None:
    return await db.get(ChatSession, session_id)


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str, db: AsyncSession = Depends(get_db)
) -> dict[str, str]:
    session = await db.get(ChatSession, session_id)
    if session:
        await db.delete(session)
        await db.commit()
    return {"status": "ok"}


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageResponse])
async def get_messages(
    session_id: str, db: AsyncSession = Depends(get_db)
) -> list[ChatMessage]:
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
    )
    return list(result.scalars().all())
