from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel


class NoteCreate(BaseModel):
    title: str
    content: Optional[str] = ""
    tags: Optional[List[str]] = []


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None


class NoteResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    content: Optional[str] = ""
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
