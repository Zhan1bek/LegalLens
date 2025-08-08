from typing import List, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models.document import Document
from app.db.models.insight import Insight
from pydantic import BaseModel

router = APIRouter(prefix="/documents", tags=["documents"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DocumentItem(BaseModel):
    id: UUID
    filename: str
    size: int | None = None

    class Config:
        from_attributes = True


class DocumentListOut(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[DocumentItem]


@router.get("/", response_model=DocumentListOut)
def list_documents(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    q = db.query(Document)
    total = q.count()
    docs = q.offset(offset).limit(limit).all()
    return DocumentListOut(total=total, limit=limit, offset=offset, items=docs)


class InsightItem(BaseModel):
    id: UUID
    answer: Any | None = None

    class Config:
        from_attributes = True


class AnalysisStatusOut(BaseModel):
    document_id: UUID
    status: str
    insights: List[InsightItem]


@router.get("/{doc_id}/analysis", response_model=AnalysisStatusOut)
def get_analysis_status(doc_id: UUID, db: Session = Depends(get_db)):
    doc = db.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    insights = db.query(Insight).filter(Insight.document_id == doc_id).all()
    status = "processed" if insights else "not_started"
    return AnalysisStatusOut(document_id=doc_id, status=status, insights=insights)
