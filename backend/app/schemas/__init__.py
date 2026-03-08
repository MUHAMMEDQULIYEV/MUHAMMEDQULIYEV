from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.schemas.note import NoteCreate, NoteUpdate, NoteResponse
from app.schemas.flashcard import DeckCreate, DeckResponse, FlashcardCreate, FlashcardReview, FlashcardResponse
from app.schemas.vocabulary import VocabularyResponse, YouTubeExtractRequest, UploadTranscriptRequest, VocabularyCreate
from app.schemas.analytics import (
    ProductivityAnalyticsResponse,
    LanguageProgressResponse,
    DashboardResponse,
    RecommendationResponse,
)

__all__ = [
    "TaskCreate", "TaskUpdate", "TaskResponse",
    "NoteCreate", "NoteUpdate", "NoteResponse",
    "DeckCreate", "DeckResponse", "FlashcardCreate", "FlashcardReview", "FlashcardResponse",
    "VocabularyResponse", "YouTubeExtractRequest", "UploadTranscriptRequest", "VocabularyCreate",
    "ProductivityAnalyticsResponse", "LanguageProgressResponse", "DashboardResponse", "RecommendationResponse",
]
