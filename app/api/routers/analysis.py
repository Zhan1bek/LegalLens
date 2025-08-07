from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.document import Document
from app.api.schemas import InsightOut
from app.services.analysis import analyze_and_save

router = APIRouter(prefix="/documents", tags=["documents"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/{doc_id}/analyze", response_model=InsightOut)
async def analyze_document(doc_id: UUID, db: Session = Depends(get_db)):
    doc = db.get(Document, doc_id)
    if not doc:
        raise HTTPException(404, "Document not found")

    answer = await analyze_and_save(db, doc)
    return {"answer": answer}
