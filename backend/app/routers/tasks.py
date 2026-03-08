from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone, timedelta

from app.database import get_db
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.utils.helpers import get_default_user

router = APIRouter()


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(task_in: TaskCreate, db: AsyncSession = Depends(get_db)):
    user = await get_default_user(db)
    task = Task(
        user_id=user.id,
        **task_in.model_dump(),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(task)
    await db.flush()
    await db.refresh(task)
    return task


@router.get("/upcoming", response_model=List[TaskResponse])
async def get_upcoming_tasks(db: AsyncSession = Depends(get_db)):
    user = await get_default_user(db)
    now = datetime.now(timezone.utc)
    cutoff = now + timedelta(hours=24)
    result = await db.execute(
        select(Task)
        .where(Task.user_id == user.id)
        .where(Task.deadline >= now)
        .where(Task.deadline <= cutoff)
        .order_by(Task.deadline)
    )
    return result.scalars().all()


@router.get("", response_model=List[TaskResponse])
async def list_tasks(
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    user = await get_default_user(db)
    query = select(Task).where(Task.user_id == user.id)
    if status:
        query = query.where(Task.status == status)
    if category:
        query = query.where(Task.category == category)
    if priority:
        query = query.where(Task.priority == priority)
    query = query.order_by(Task.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: UUID, db: AsyncSession = Depends(get_db)):
    user = await get_default_user(db)
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == user.id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: UUID, task_in: TaskUpdate, db: AsyncSession = Depends(get_db)):
    user = await get_default_user(db)
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == user.id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    task.updated_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: UUID, db: AsyncSession = Depends(get_db)):
    user = await get_default_user(db)
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == user.id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await db.delete(task)
