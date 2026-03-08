from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class VocabularyResponse(BaseModel):
    id: UUID
    user_id: UUID
    word: str
    language: str
    translation: Optional[str] = ""
    frequency_count: int = 1
    source_url: Optional[str] = None
    learned: bool = False
    date_learned: Optional[datetime] = None
    pos: Optional[str] = None
    difficulty: int = 1
    created_at: datetime

    model_config = {"from_attributes": True}


class YouTubeExtractRequest(BaseModel):
    url: str
    language: str = "english"


class UploadTranscriptRequest(BaseModel):
    content: str
    language: str = "english"
    source_url: Optional[str] = None


class VocabularyCreate(BaseModel):
    word: str
    language: str = "english"
    translation: Optional[str] = ""
    frequency_count: int = 1
    source_url: Optional[str] = None
    pos: Optional[str] = None
    difficulty: int = 1
