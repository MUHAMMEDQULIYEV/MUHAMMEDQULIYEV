from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from app.models.flashcard import DeckLanguage, DeckSourceType


class DeckCreate(BaseModel):
    name: str
    language: DeckLanguage = DeckLanguage.english
    source_type: DeckSourceType = DeckSourceType.manual


class DeckResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    language: DeckLanguage
    source_type: DeckSourceType
    created_at: datetime

    model_config = {"from_attributes": True}


class FlashcardCreate(BaseModel):
    deck_id: UUID
    front: str
    back: str


class FlashcardReview(BaseModel):
    quality: int  # 0-5


class FlashcardResponse(BaseModel):
    id: UUID
    deck_id: UUID
    front: str
    back: str
    ease_factor: float
    interval: int
    repetitions: int
    last_reviewed: Optional[datetime] = None
    next_review: Optional[datetime] = None

    model_config = {"from_attributes": True}
