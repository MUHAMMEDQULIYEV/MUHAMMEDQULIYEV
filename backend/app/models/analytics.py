import uuid
from datetime import datetime, timezone, date as date_type
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class ProductivityAnalytics(Base):
    __tablename__ = "productivity_analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    tasks_completed = Column(Integer, default=0)
    tasks_total = Column(Integer, default=0)
    category_breakdown = Column(JSONB, default={})
    time_spent = Column(JSONB, default={})
    completion_rate = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="analytics")


class LanguageProgress(Base):
    __tablename__ = "language_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    language = Column(String(20), nullable=False)
    date = Column(Date, nullable=False)
    words_learned = Column(Integer, default=0)
    flashcard_accuracy = Column(Float, default=0.0)
    time_spent = Column(Integer, default=0)  # minutes
    topics_studied = Column(JSONB, default=[])
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="language_progress")
