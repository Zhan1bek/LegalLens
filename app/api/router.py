from uuid import UUID
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models.document import Document
from app.db.models.insight import DocumentInsight
from app.api.schemas import InsightOut
from app.services.llm import analyze_text

router = APIRouter(prefix="/documents", tags=["documents"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/{doc_id}/analyze", response_model=InsightOut)
async def analyze_document(
    doc_id: UUID,
    db: Session = Depends(get_db),
):
    doc = db.get(Document, doc_id)
    if not doc:
        raise HTTPException(404, detail="Document not found")

    data = await analyze_text(doc.content)

    insight = DocumentInsight(
        document_id=doc.id,
        summary=data["summary"],
        risks=json.dumps(data["risks"], ensure_ascii=False),
    )
    db.add(insight)
    db.commit()
    db.refresh(insight)
    return insight
