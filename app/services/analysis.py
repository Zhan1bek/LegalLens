from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models.analysis import AnalysisRequest
from app.db.models.document import Document
from app.services.llm import analyze_text
from app.core.logging import logger


async def analyze_and_save(db: Session, doc: Document) -> str:
    ar = db.execute(
        select(AnalysisRequest).where(AnalysisRequest.document_id == doc.id)
    ).scalar_one_or_none()
    if ar is None:
        ar = AnalysisRequest(document_id=doc.id)
        db.add(ar)

    ar.status = "pending"
    ar.error = None
    db.commit()
    db.refresh(ar)

    try:
        answer = await analyze_text(doc.content)
        ar.raw_json = answer
        ar.status = "success"
        logger.info("analysis %s success", ar.id)
    except Exception as exc:
        ar.status = "failed"
        ar.error = str(exc)
        logger.exception("analysis %s failed: %s", ar.id, exc)
        raise
    finally:
        db.commit()

    return answer
