from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.sql import func
from app.db.base import Base


class AnalysisRequest(Base):
    __tablename__ = "analysis_requests"

    id = Column(Integer, primary_key=True)
    document_id = Column(ForeignKey("documents.id"), unique=True, index=True)
    status = Column(String, default="pending")
    raw_json = Column(JSON, nullable=True)
    normalized = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
