import uuid
from datetime import datetime, timezone
import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class VocabLanguage(str, enum.Enum):
    english = "english"
    korean = "korean"


class LanguageVocabulary(Base):
    __tablename__ = "language_vocabulary"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    word = Column(String(255), nullable=False)
    language = Column(String(20), nullable=False, default=VocabLanguage.english)
    translation = Column(String(500), nullable=True, default="")
    frequency_count = Column(Integer, default=1)
    source_url = Column(String(1000), nullable=True)
    learned = Column(Boolean, default=False)
    date_learned = Column(DateTime(timezone=True), nullable=True)
    pos = Column(String(50), nullable=True)  # Part of speech
    difficulty = Column(Integer, default=1)  # 1-5 scale
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="vocabulary")
