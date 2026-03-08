from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from app.models.task import TaskCategory, TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: TaskCategory = TaskCategory.personal
    deadline: Optional[datetime] = None
    priority: TaskPriority = TaskPriority.medium
    status: TaskStatus = TaskStatus.not_started
    estimated_duration: Optional[int] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[TaskCategory] = None
    deadline: Optional[datetime] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    estimated_duration: Optional[int] = None


class TaskResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str] = None
    category: TaskCategory
    deadline: Optional[datetime] = None
    priority: TaskPriority
    status: TaskStatus
    estimated_duration: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
