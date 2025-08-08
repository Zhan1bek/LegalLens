from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List


class DocumentOut(BaseModel):
    id: UUID
    original_name: str
    mime_type: str
    size_bytes: int = Field(..., ge=0)
    uploaded_at: datetime

    class Config:
        from_attributes = True


class DocumentInsightOut(BaseModel):
    id: UUID
    document_id: UUID
    summary: str
    risks: str
    created_at: datetime

    class Config:
        from_attributes = True


class AnalysisStatusOut(BaseModel):
    document_id: UUID
    status: str
    latest: DocumentInsightOut | None = None
    history: List[DocumentInsightOut] = []


class ConversationOut(BaseModel):
    id: UUID
    document_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class ChatMessageIn(BaseModel):
    question: str


class ChatMessageOut(BaseModel):
    answer: str
    citations: list[dict] = []
