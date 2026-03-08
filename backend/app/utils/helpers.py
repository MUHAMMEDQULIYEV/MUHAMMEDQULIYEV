from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from app.models.user import User
from app.config import settings


async def get_default_user(db: AsyncSession) -> User:
    """Get the default single user for this local setup."""
    result = await db.execute(select(User).limit(1))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=503,
            detail="No user found. Application is still initializing.",
        )
    return user
