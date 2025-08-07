from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.services.documents import create_document
from app.api.schemas import DocumentOut

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
