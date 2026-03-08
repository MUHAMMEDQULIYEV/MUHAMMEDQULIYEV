from datetime import date, datetime
from typing import Optional, Dict, List, Any
from uuid import UUID
from pydantic import BaseModel


class ProductivityAnalyticsResponse(BaseModel):
    id: UUID
    user_id: UUID
    date: date
    tasks_completed: int
    tasks_total: int
    category_breakdown: Dict[str, Any] = {}
    time_spent: Dict[str, Any] = {}
    completion_rate: float

    model_config = {"from_attributes": True}


class LanguageProgressResponse(BaseModel):
    id: UUID
    user_id: UUID
    language: str
    date: date
    words_learned: int
    flashcard_accuracy: float
    time_spent: int
    topics_studied: List[str] = []

    model_config = {"from_attributes": True}


class DashboardResponse(BaseModel):
    tasks_today: int
    tasks_completed_today: int
    words_learned_this_week: int
    upcoming_deadlines: List[Dict[str, Any]]
    productivity_streak: int
    recent_analytics: List[Dict[str, Any]]


class RecommendationResponse(BaseModel):
    best_hour: Optional[int] = None
    best_day: Optional[str] = None
    top_category: Optional[str] = None
    procrastination_index: float = 0.0
    suggestions: List[str] = []
    chart_data: Dict[str, Any] = {}
