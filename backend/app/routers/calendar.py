from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

from app.services import calendar_service

router = APIRouter()


class SyncRequest(BaseModel):
    token_data: Optional[Dict[str, Any]] = None


class TaskToEventRequest(BaseModel):
    task_id: str
    title: str
    description: Optional[str] = ""
    start_dt: datetime
    end_dt: datetime


@router.post("/sync")
async def sync_calendar(request: SyncRequest):
    """Sync with Google Calendar."""
    events = calendar_service.sync_calendar_events(request.token_data)
    return {"events": events, "count": len(events)}


@router.post("/task-to-event")
async def task_to_event(request: TaskToEventRequest):
    """Create a Google Calendar event from a task."""
    result = calendar_service.create_calendar_event(
        title=request.title,
        description=request.description or "",
        start_dt=request.start_dt,
        end_dt=request.end_dt,
        token_data=None,
    )
    return result


@router.get("/events")
async def get_calendar_events():
    """Get upcoming Google Calendar events."""
    events = calendar_service.get_upcoming_events()
    return {"events": events}
