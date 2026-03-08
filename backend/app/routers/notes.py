from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone

from app.database import get_db
from app.models.note import Note
from app.schemas.note import NoteCreate, NoteUpdate, NoteResponse
from app.utils.helpers import get_default_user

router = APIRouter()


@router.post("", response_model=NoteResponse, status_code=201)
async def create_note(note_in: NoteCreate, db: AsyncSession = Depends(get_db)):
    user = await get_default_user(db)
    note = Note(
        user_id=user.id,
        **note_in.model_dump(),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(note)
    await db.flush()
    await db.refresh(note)
    return note


@router.get("/search", response_model=List[NoteResponse])
async def search_notes(q: str = Query(...), db: AsyncSession = Depends(get_db)):
    user = await get_default_user(db)
    result = await db.execute(
        select(Note)
        .where(Note.user_id == user.id)
        .where(
            or_(
                Note.title.ilike(f"%{q}%"),
                Note.content.ilike(f"%{q}%"),
            )
        )
        .order_by(Note.updated_at.desc())
    )
    return result.scalars().all()


@router.get("", response_model=List[NoteResponse])
async def list_notes(db: AsyncSession = Depends(get_db)):
    user = await get_default_user(db)
    result = await db.execute(
        select(Note)
        .where(Note.user_id == user.id)
        .order_by(Note.updated_at.desc())
    )
    return result.scalars().all()


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(note_id: UUID, note_in: NoteUpdate, db: AsyncSession = Depends(get_db)):
    user = await get_default_user(db)
    result = await db.execute(
        select(Note).where(Note.id == note_id, Note.user_id == user.id)
    )
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    update_data = note_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(note, field, value)
    note.updated_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(note)
    return note


@router.delete("/{note_id}", status_code=204)
async def delete_note(note_id: UUID, db: AsyncSession = Depends(get_db)):
    user = await get_default_user(db)
    result = await db.execute(
        select(Note).where(Note.id == note_id, Note.user_id == user.id)
    )
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    await db.delete(note)
