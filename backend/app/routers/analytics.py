from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta, date

from app.database import get_db
from app.models.task import Task, TaskStatus
from app.models.analytics import ProductivityAnalytics, LanguageProgress
from app.models.vocabulary import LanguageVocabulary
from app.services import ml_service
from app.utils.helpers import get_default_user

router = APIRouter()


@router.get("/productivity")
async def productivity_analytics(db: AsyncSession = Depends(get_db)):
    user = await get_default_user(db)

    result = await db.execute(
        select(ProductivityAnalytics)
        .where(ProductivityAnalytics.user_id == user.id)
        .order_by(ProductivityAnalytics.date.desc())
        .limit(30)
    )
    records = result.scalars().all()

    records_dict = [
        {
            "date": r.date,
            "tasks_completed": r.tasks_completed,
            "tasks_total": r.tasks_total,
            "category_breakdown": r.category_breakdown,
            "completion_rate": r.completion_rate,
        }
        for r in records
    ]

    analysis = ml_service.analyze_productivity(records_dict)

    return {
        "records": records_dict,
        "analysis": analysis,
    }


@router.get("/language")
async def language_analytics(db: AsyncSession = Depends(get_db)):
    user = await get_default_user(db)

    result = await db.execute(
        select(LanguageProgress)
        .where(LanguageProgress.user_id == user.id)
        .order_by(LanguageProgress.date.desc())
        .limit(30)
    )
    records = result.scalars().all()

    # Count total vocabulary per language
    total_vocab_result = await db.execute(
        select(LanguageVocabulary.language, func.count(LanguageVocabulary.id).label("total"))
        .where(LanguageVocabulary.user_id == user.id)
        .group_by(LanguageVocabulary.language)
    )
    # Count learned vocabulary per language
    learned_vocab_result = await db.execute(
        select(LanguageVocabulary.language, func.count(LanguageVocabulary.id).label("learned"))
        .where(LanguageVocabulary.user_id == user.id)
        .where(LanguageVocabulary.learned == True)
        .group_by(LanguageVocabulary.language)
    )

    vocab_by_lang: Dict[str, Any] = {}
    for row in total_vocab_result.all():
        vocab_by_lang[row[0]] = {"total": row[1], "learned": 0}
    for row in learned_vocab_result.all():
        if row[0] in vocab_by_lang:
            vocab_by_lang[row[0]]["learned"] = row[1]
        else:
            vocab_by_lang[row[0]] = {"total": 0, "learned": row[1]}

    return {
        "records": [
            {
                "language": r.language,
                "date": r.date.isoformat(),
                "words_learned": r.words_learned,
                "flashcard_accuracy": r.flashcard_accuracy,
                "time_spent": r.time_spent,
            }
            for r in records
        ],
        "vocabulary_summary": vocab_by_lang,
    }


@router.get("/dashboard")
async def dashboard_analytics(db: AsyncSession = Depends(get_db)):
    user = await get_default_user(db)
    now = datetime.now(timezone.utc)
    today = now.date()
    week_start = today - timedelta(days=7)

    # Tasks today
    tasks_result = await db.execute(
        select(func.count(Task.id)).where(Task.user_id == user.id)
    )
    total_tasks = tasks_result.scalar() or 0

    completed_result = await db.execute(
        select(func.count(Task.id))
        .where(Task.user_id == user.id)
        .where(Task.status == TaskStatus.completed)
    )
    completed_tasks = completed_result.scalar() or 0

    # Words learned this week
    words_result = await db.execute(
        select(func.count(LanguageVocabulary.id))
        .where(LanguageVocabulary.user_id == user.id)
        .where(LanguageVocabulary.learned == True)
        .where(LanguageVocabulary.date_learned >= datetime.combine(week_start, datetime.min.time()).replace(tzinfo=timezone.utc))
    )
    words_this_week = words_result.scalar() or 0

    # Upcoming deadlines
    deadlines_result = await db.execute(
        select(Task)
        .where(Task.user_id == user.id)
        .where(Task.deadline >= now)
        .where(Task.deadline <= now + timedelta(days=7))
        .where(Task.status.in_(["not_started", "in_progress"]))
        .order_by(Task.deadline)
        .limit(5)
    )
    upcoming = deadlines_result.scalars().all()

    return {
        "tasks_total": total_tasks,
        "tasks_completed": completed_tasks,
        "words_learned_this_week": words_this_week,
        "completion_rate": round(completed_tasks / total_tasks * 100, 1) if total_tasks > 0 else 0.0,
        "upcoming_deadlines": [
            {
                "id": str(t.id),
                "title": t.title,
                "deadline": t.deadline.isoformat() if t.deadline else None,
                "priority": t.priority,
                "category": t.category,
            }
            for t in upcoming
        ],
    }


@router.get("/recommendations")
async def get_recommendations(db: AsyncSession = Depends(get_db)):
    user = await get_default_user(db)

    analytics_result = await db.execute(
        select(ProductivityAnalytics)
        .where(ProductivityAnalytics.user_id == user.id)
        .order_by(ProductivityAnalytics.date.desc())
        .limit(30)
    )
    analytics_records = analytics_result.scalars().all()

    lang_result = await db.execute(
        select(LanguageProgress)
        .where(LanguageProgress.user_id == user.id)
        .order_by(LanguageProgress.date.desc())
        .limit(30)
    )
    lang_records = lang_result.scalars().all()

    analytics_dict = [
        {
            "date": r.date,
            "tasks_completed": r.tasks_completed,
            "tasks_total": r.tasks_total,
            "category_breakdown": r.category_breakdown,
            "completion_rate": r.completion_rate,
        }
        for r in analytics_records
    ]

    lang_dict = [
        {"words_learned": r.words_learned, "flashcard_accuracy": r.flashcard_accuracy}
        for r in lang_records
    ]

    analysis = ml_service.analyze_productivity(analytics_dict)
    recommendations = ml_service.generate_recommendations(analysis, lang_dict)

    return recommendations
