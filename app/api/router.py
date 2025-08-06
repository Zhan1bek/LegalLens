# app/api/router.py
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.document import Document
from app.api.schemas import InsightOut
from app.services.llm import analyze_text

router = APIRouter(prefix="/documents", tags=["documents"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/documents/{doc_id}/analyze", response_model=InsightOut)
async def analyze_document(doc_id: UUID, db: Session = Depends(get_db)):
    doc = db.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    answer = await analyze_text(doc.content)  # ← просто await
    return {"answer": answer}
