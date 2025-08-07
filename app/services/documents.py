import mimetypes
import shutil
import uuid
from pathlib import Path
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException

from app.core.config import get_settings
from app.db.models.document import Document
from app.utils.parser import extract_text
from app.core.logging import logger

settings = get_settings()
STORAGE_PATH = Path(__file__).resolve().parents[2] / "storage"


def _validate_mime(file: UploadFile) -> str:
    mime = file.content_type or mimetypes.guess_type(file.filename)[0]
    if mime not in {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
        "text/plain",
    }:
        raise HTTPException(415, f"Unsupported mime-type: {mime}")
    return mime


def save_file_to_disk(file: UploadFile) -> Path:
    dst_name = f"{uuid.uuid4()}_{file.filename}"
    dst_path = STORAGE_PATH / dst_name
    with dst_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return dst_path


def create_document(db: Session, file: UploadFile) -> Document:
    mime = _validate_mime(file)
    path = save_file_to_disk(file)

    text = extract_text(path, mime)
    size = path.stat().st_size

    doc = Document(
        original_name=file.filename,
        mime_type=mime,
        file_path=str(path),
        size_bytes=size,
        content=text,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    logger.info("Document {id} saved, {size} bytes", id=doc.id, size=size)
    return doc
