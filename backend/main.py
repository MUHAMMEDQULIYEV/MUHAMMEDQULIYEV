from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import engine, Base
from app.config import settings
from app.routers import tasks, notes, flashcards, language, analytics, notifications, calendar
from app.services.email_service import start_scheduler, stop_scheduler
from app import models  # noqa: F401 – ensure models are registered


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create default user on startup
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select
    from app.models.user import User
    import uuid

    async with AsyncSession(engine) as session:
        result = await session.execute(select(User).limit(1))
        user = result.scalar_one_or_none()
        if user is None:
            default_user = User(
                id=uuid.uuid4(),
                email=settings.DEFAULT_USER_EMAIL,
                preferences={"notifications": True, "theme": "dark", "language": "english"},
            )
            session.add(default_user)
            await session.commit()

    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="Productivity & Language Learning Platform",
    description="A self-hosted platform combining task management, notes, flashcards, and language learning.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(notes.router, prefix="/api/notes", tags=["Notes"])
app.include_router(flashcards.router, prefix="/api", tags=["Flashcards"])
app.include_router(language.router, prefix="/api/language", tags=["Language"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(calendar.router, prefix="/api/calendar", tags=["Calendar"])


@app.get("/api/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}
