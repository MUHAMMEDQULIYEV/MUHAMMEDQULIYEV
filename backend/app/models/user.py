import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    preferences = Column(JSONB, default={"notifications": True, "theme": "dark", "language": "english"})

    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="user", cascade="all, delete-orphan")
    decks = relationship("FlashcardDeck", back_populates="user", cascade="all, delete-orphan")
    vocabulary = relationship("LanguageVocabulary", back_populates="user", cascade="all, delete-orphan")
    analytics = relationship("ProductivityAnalytics", back_populates="user", cascade="all, delete-orphan")
    language_progress = relationship("LanguageProgress", back_populates="user", cascade="all, delete-orphan")
