from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.session import SessionLocal
from app.db.models.document import Document
from app.db.models.conversation import Conversation, Message
from app.api.schemas import ConversationOut, ChatMessageIn, ChatMessageOut
from app.services.chat import answer_on_document, save_message

router = APIRouter(prefix="/conversations", tags=["chat"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=ConversationOut, status_code=201)
def create_conversation(document_id: UUID, db: Session = Depends(get_db)):
    doc = db.get(Document, document_id)
    if not doc:
        raise HTTPException(404, "Document not found")
    conv = Conversation(document_id=document_id)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv


@router.get("/{conv_id}/messages")
def get_messages(conv_id: UUID, db: Session = Depends(get_db)):
    conv = db.get(Conversation, conv_id)
    if not conv:
        raise HTTPException(404, "Conversation not found")
    stmt = (
        select(Message)
        .where(Message.conversation_id == conv_id)
        .order_by(Message.created_at.asc())
    )
    return db.scalars(stmt).all()


@router.post("/{conv_id}/messages", response_model=ChatMessageOut)
async def ask(conv_id: UUID, payload: ChatMessageIn, db: Session = Depends(get_db)):
    conv = db.get(Conversation, conv_id)
    if not conv:
        raise HTTPException(404, "Conversation not found")
    save_message(db, conv, "user", payload.question)
    answer, citations = await answer_on_document(db, conv, payload.question)
    save_message(db, conv, "assistant", answer)
    return ChatMessageOut(answer=answer, citations=citations)
