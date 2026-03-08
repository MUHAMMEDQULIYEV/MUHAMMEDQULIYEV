"""
Email service using SMTP + APScheduler for scheduled notifications.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.config import settings

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()


def send_email(to_email: str, subject: str, html_body: str) -> bool:
    """Send an HTML email via SMTP."""
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning("SMTP credentials not configured; skipping email send.")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_USER
        msg["To"] = to_email

        part = MIMEText(html_body, "html")
        msg.attach(part)

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, to_email, msg.as_string())

        logger.info("Email sent to %s: %s", to_email, subject)
        return True
    except Exception as exc:
        logger.error("Failed to send email to %s: %s", to_email, exc)
        return False


def _task_reminder_job():
    """Check for tasks due within 1 hour and send reminders."""
    import asyncio
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select
    from app.database import engine
    from app.models.task import Task
    from app.models.user import User

    async def _run():
        now = datetime.now(timezone.utc)
        one_hour_later = now + timedelta(hours=1)

        async with AsyncSession(engine) as session:
            result = await session.execute(
                select(Task, User)
                .join(User, Task.user_id == User.id)
                .where(Task.deadline >= now)
                .where(Task.deadline <= one_hour_later)
                .where(Task.status.in_(["not_started", "in_progress"]))
            )
            rows = result.all()

        for task, user in rows:
            html = f"""
            <html><body>
            <h2>⏰ Task Reminder</h2>
            <p>Your task <strong>{task.title}</strong> is due in less than 1 hour!</p>
            <p>Priority: {task.priority} | Category: {task.category}</p>
            <p>Deadline: {task.deadline.strftime('%Y-%m-%d %H:%M UTC')}</p>
            </body></html>
            """
            send_email(user.email, f"⏰ Reminder: {task.title}", html)

    asyncio.run(_run())


def _daily_summary_job():
    """Send daily summary email at 8 AM."""
    import asyncio
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select, func
    from app.database import engine
    from app.models.task import Task, TaskStatus
    from app.models.user import User
    from datetime import date

    async def _run():
        today = date.today()

        async with AsyncSession(engine) as session:
            users_result = await session.execute(select(User))
            users = users_result.scalars().all()

        for user in users:
            async with AsyncSession(engine) as session:
                total = await session.execute(
                    select(func.count(Task.id)).where(Task.user_id == user.id)
                )
                completed = await session.execute(
                    select(func.count(Task.id))
                    .where(Task.user_id == user.id)
                    .where(Task.status == TaskStatus.completed)
                )
                total_count = total.scalar() or 0
                completed_count = completed.scalar() or 0

            html = f"""
            <html><body>
            <h2>📊 Daily Summary - {today}</h2>
            <p>Hello! Here's your productivity summary for today:</p>
            <ul>
              <li>Total Tasks: {total_count}</li>
              <li>Completed: {completed_count}</li>
              <li>Completion Rate: {(completed_count / total_count * 100):.1f}% if total_count > 0 else 0%</li>
            </ul>
            <p>Keep up the great work! 🚀</p>
            </body></html>
            """
            send_email(user.email, f"📊 Daily Summary - {today}", html)

    asyncio.run(_run())


def _weekly_report_job():
    """Send weekly productivity report every Monday at 8 AM."""
    import asyncio
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select
    from app.database import engine
    from app.models.analytics import ProductivityAnalytics
    from app.models.user import User
    from datetime import date, timedelta

    async def _run():
        week_start = date.today() - timedelta(days=7)

        async with AsyncSession(engine) as session:
            users_result = await session.execute(select(User))
            users = users_result.scalars().all()

        for user in users:
            async with AsyncSession(engine) as session:
                analytics_result = await session.execute(
                    select(ProductivityAnalytics)
                    .where(ProductivityAnalytics.user_id == user.id)
                    .where(ProductivityAnalytics.date >= week_start)
                    .order_by(ProductivityAnalytics.date)
                )
                records = analytics_result.scalars().all()

            total_completed = sum(r.tasks_completed for r in records)
            total_tasks = sum(r.tasks_total for r in records)
            avg_rate = (total_completed / total_tasks * 100) if total_tasks > 0 else 0

            html = f"""
            <html><body>
            <h2>📈 Weekly Productivity Report</h2>
            <p>Week of {week_start} - {date.today()}</p>
            <ul>
              <li>Tasks Completed: {total_completed}</li>
              <li>Total Tasks: {total_tasks}</li>
              <li>Average Completion Rate: {avg_rate:.1f}%</li>
            </ul>
            <p>Keep pushing forward! 💪</p>
            </body></html>
            """
            send_email(user.email, "📈 Weekly Productivity Report", html)

    asyncio.run(_run())


def start_scheduler():
    """Start the APScheduler background scheduler."""
    if not scheduler.running:
        scheduler.add_job(
            _task_reminder_job,
            trigger=IntervalTrigger(hours=1),
            id="task_reminder",
            replace_existing=True,
            misfire_grace_time=300,
        )
        scheduler.add_job(
            _daily_summary_job,
            trigger=CronTrigger(hour=8, minute=0),
            id="daily_summary",
            replace_existing=True,
        )
        scheduler.add_job(
            _weekly_report_job,
            trigger=CronTrigger(day_of_week="mon", hour=8, minute=0),
            id="weekly_report",
            replace_existing=True,
        )
        scheduler.start()
        logger.info("Email scheduler started.")


def stop_scheduler():
    """Stop the APScheduler background scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Email scheduler stopped.")
