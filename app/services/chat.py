from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.db.models.chunk import DocumentChunk
from app.db.models.conversation import Conversation, Message
from app.services.embeddings import embed
from app.services.llm import analyze_text

SYSTEM_RULES = (
    "You are LegalLens AI. Answer only from the provided context. "
    "If the answer is not in the context, say you do not have enough information."
)


def _retrieve(db: Session, document_id, query: str, k: int = 5):
    q_vec = embed(query)
    # cosine_distance на стороне БД
    dist = func.cosine_distance(DocumentChunk.embedding, q_vec)
    stmt = (
        select(DocumentChunk, dist.label("distance"))
        .where(DocumentChunk.document_id == document_id)
        .order_by("distance")
        .limit(k)
    )
    rows = db.execute(stmt).all()
    chunks = [row[0] for row in rows]
    return chunks


async def answer_on_document(
    db: Session, conv: Conversation, question: str
) -> tuple[str, list[dict]]:
    chunks = _retrieve(db, conv.document_id, question, k=5)
    context = "\n\n---\n\n".join(c.text for c in chunks)
    prompt = f"{SYSTEM_RULES}\n\nContext:\n{context}\n\nQuestion:\n{question}"
    answer = await analyze_text(prompt)
    citations = [{"chunk_id": c.id, "chunk_index": c.chunk_index} for c in chunks]
    return answer, citations


def save_message(db: Session, conv: Conversation, role: str, content: str) -> Message:
    msg = Message(conversation_id=conv.id, role=role, content=content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg
