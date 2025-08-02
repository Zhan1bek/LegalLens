from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class DocumentOut(BaseModel):
    id: UUID
    original_name: str
    mime_type: str
    size_bytes: int = Field(..., ge=0)
    uploaded_at: datetime

    class Config:
        from_attributes = True


class InsightOut(BaseModel):
    id: UUID
    document_id: UUID
    summary: str
    risks: list[str]
    created_at: datetime

    class Config:
        from_attributes = True
