from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.services.email_service import send_email, scheduler
from app.utils.helpers import get_default_user

router = APIRouter()


class NotificationSettings(BaseModel):
    email_enabled: bool = True
    daily_summary: bool = True
    task_reminders: bool = True
    weekly_report: bool = True


class SendEmailRequest(BaseModel):
    to_email: str
    subject: str
    body: str


@router.post("/settings")
async def update_notification_settings(
    settings_in: NotificationSettings,
    db: AsyncSession = Depends(get_db),
):
    user = await get_default_user(db)
    prefs = user.preferences or {}
    prefs["notifications"] = settings_in.model_dump()
    user.preferences = prefs
    await db.flush()
    return {"status": "ok", "preferences": prefs}


@router.get("/queue")
async def get_notification_queue():
    """Get pending scheduled jobs from APScheduler."""
    jobs = []
    for job in scheduler.get_jobs():
        next_run = job.next_run_time
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": next_run.isoformat() if next_run else None,
        })
    return {"scheduled_jobs": jobs}


@router.post("/send-email")
async def manually_send_email(request: SendEmailRequest):
    """Manually trigger an email send."""
    html_body = f"<html><body><p>{request.body}</p></body></html>"
    success = send_email(request.to_email, request.subject, html_body)
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to send email. Check SMTP configuration.",
        )
    return {"status": "sent", "to": request.to_email}
