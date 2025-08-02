from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import mimetypes
from pathlib import Path
import uuid
import shutil

from app.db.session import SessionLocal
from app.db.models.document import Document
from app.utils.parser import extract_text
from app.api.schemas import DocumentOut

STORAGE_PATH = Path(__file__).resolve().parents[1] / "storage"

app = FastAPI(title="LegalLens AI")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/upload", response_model=DocumentOut)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(400, detail="No filename")

    mime = file.content_type or mimetypes.guess_type(file.filename)[0]
    if mime not in {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
        "text/plain",
    }:
        raise HTTPException(415, detail=f"Unsupported mime-type: {mime}")

    dst_name = f"{uuid.uuid4()}_{file.filename}"
    dst_path = STORAGE_PATH / dst_name
    with dst_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    size = dst_path.stat().st_size

    text = extract_text(dst_path, mime)

    doc = Document(
        original_name=file.filename,
        mime_type=mime,
        file_path=str(dst_path),
        size_bytes=size,
        content=text,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return doc
