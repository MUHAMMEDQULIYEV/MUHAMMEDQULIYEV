import uuid
from datetime import datetime, timezone
import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class DeckLanguage(str, enum.Enum):
    english = "english"
    korean = "korean"


class DeckSourceType(str, enum.Enum):
    youtube = "youtube"
    manual = "manual"
    upload = "upload"


class FlashcardDeck(Base):
    __tablename__ = "flashcard_decks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    language = Column(SAEnum(DeckLanguage), nullable=False, default=DeckLanguage.english)
    source_type = Column(SAEnum(DeckSourceType), nullable=False, default=DeckSourceType.manual)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="decks")
    cards = relationship("Flashcard", back_populates="deck", cascade="all, delete-orphan")


class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deck_id = Column(UUID(as_uuid=True), ForeignKey("flashcard_decks.id", ondelete="CASCADE"), nullable=False)
    front = Column(String(1000), nullable=False)
    back = Column(String(1000), nullable=False)
    ease_factor = Column(Float, default=2.5)
    interval = Column(Integer, default=1)  # days
    repetitions = Column(Integer, default=0)
    last_reviewed = Column(DateTime(timezone=True), nullable=True)
    next_review = Column(DateTime(timezone=True), nullable=True)

    deck = relationship("FlashcardDeck", back_populates="cards")
