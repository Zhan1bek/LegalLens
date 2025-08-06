from sqlalchemy.dialects.postgresql import UUID  # +
from sqlalchemy import BigInteger, Column, Integer, Text, ForeignKey
from pgvector.sqlalchemy import Vector
from app.db.base import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    document_id = Column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE")  # ← UUID
    )
    chunk_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    embedding = Column(Vector(768), nullable=False)
