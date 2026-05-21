import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_serializer


class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str
    url: str | None = None


class Citation(BaseModel):
    url: str | None = None
    title: str | None = None
    content: str | None = None


class ChatSessionResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    title: str
    created_at: datetime
    updated_at: datetime

    @field_serializer("id")
    def serialize_id(self, value: uuid.UUID) -> str:
        return str(value)


class ChatMessageResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    session_id: uuid.UUID
    role: str
    content: str
    citations: list[Citation] | None = None
    created_at: datetime

    @field_serializer("id", "session_id")
    def serialize_uuid(self, value: uuid.UUID) -> str:
        return str(value)


class SessionCreate(BaseModel):
    title: str = "New Chat"
