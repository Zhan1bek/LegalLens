from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models.document import Document
from app.api.schemas import DocumentInsightOut
from app.services.analysis import analyze_and_save  # см. ниже

router = APIRouter(prefix="/documents", tags=["analysis"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/{doc_id}/analyze", response_model=DocumentInsightOut)
async def analyze_document(doc_id: UUID, db: Session = Depends(get_db)):
    doc = db.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    insight = await analyze_and_save(db, doc)
    return insight
