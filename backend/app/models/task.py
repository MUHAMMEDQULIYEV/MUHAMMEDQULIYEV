import uuid
from datetime import datetime, timezone
import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Enum as SAEnum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class TaskCategory(str, enum.Enum):
    work = "work"
    study = "study"
    learning = "learning"
    personal = "personal"


class TaskPriority(str, enum.Enum):
    high = "high"
    medium = "medium"
    low = "low"


class TaskStatus(str, enum.Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"
    archived = "archived"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(SAEnum(TaskCategory), nullable=False, default=TaskCategory.personal)
    deadline = Column(DateTime(timezone=True), nullable=True)
    priority = Column(SAEnum(TaskPriority), nullable=False, default=TaskPriority.medium)
    status = Column(SAEnum(TaskStatus), nullable=False, default=TaskStatus.not_started)
    estimated_duration = Column(Integer, nullable=True)  # minutes
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = relationship("User", back_populates="tasks")
