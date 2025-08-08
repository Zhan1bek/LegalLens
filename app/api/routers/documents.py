from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID

from app.db.session import SessionLocal
from app.services.documents import create_document
from app.api.schemas import DocumentOut, AnalysisStatusOut, DocumentInsightOut
from app.db.models.document import Document
from app.db.models.insight import DocumentInsight

router = APIRouter(prefix="/documents", tags=["documents"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=DocumentOut, status_code=201)
async def upload(file: UploadFile = File(...), db: Session = Depends(get_db)):
    return create_document(db, file)


@router.get("/", response_model=list[DocumentOut])
def list_documents(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    stmt = (
        select(Document)
        .order_by(Document.uploaded_at.desc())
        .offset(offset)
        .limit(limit)
    )
    items = db.scalars(stmt).all()
    return items


@router.get("/{doc_id}/analysis", response_model=AnalysisStatusOut)
def analysis_status(doc_id: UUID, db: Session = Depends(get_db)):
    doc = db.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    stmt = (
        select(DocumentInsight)
        .where(DocumentInsight.document_id == doc_id)
        .order_by(DocumentInsight.created_at.desc())
    )
    insights = db.scalars(stmt).all()
    latest = insights[0] if insights else None
    status = "processed" if latest else "not_started"

    return AnalysisStatusOut(
        document_id=doc_id,
        status=status,
        latest=latest,
        history=insights,
    )
