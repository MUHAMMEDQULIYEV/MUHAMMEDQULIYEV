from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID
from datetime import datetime, timezone

from app.database import get_db
from app.models.flashcard import FlashcardDeck, Flashcard
from app.schemas.flashcard import (
    DeckCreate,
    DeckResponse,
    FlashcardCreate,
    FlashcardReview,
    FlashcardResponse,
)
from app.services.sm2 import calculate_sm2
from app.utils.helpers import get_default_user

router = APIRouter()


@router.post("/decks", response_model=DeckResponse, status_code=201)
async def create_deck(deck_in: DeckCreate, db: AsyncSession = Depends(get_db)):
    user = await get_default_user(db)
    deck = FlashcardDeck(
        user_id=user.id,
        **deck_in.model_dump(),
        created_at=datetime.now(timezone.utc),
    )
    db.add(deck)
    await db.flush()
    await db.refresh(deck)
    return deck


@router.get("/decks", response_model=List[DeckResponse])
async def list_decks(db: AsyncSession = Depends(get_db)):
    user = await get_default_user(db)
    result = await db.execute(
        select(FlashcardDeck)
        .where(FlashcardDeck.user_id == user.id)
        .order_by(FlashcardDeck.created_at.desc())
    )
    return result.scalars().all()


@router.post("/cards", response_model=FlashcardResponse, status_code=201)
async def create_flashcard(card_in: FlashcardCreate, db: AsyncSession = Depends(get_db)):
    user = await get_default_user(db)
    # Verify deck ownership
    deck_result = await db.execute(
        select(FlashcardDeck).where(
            FlashcardDeck.id == card_in.deck_id,
            FlashcardDeck.user_id == user.id,
        )
    )
    deck = deck_result.scalar_one_or_none()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")

    card = Flashcard(
        deck_id=card_in.deck_id,
        front=card_in.front,
        back=card_in.back,
        ease_factor=2.5,
        interval=1,
        repetitions=0,
        next_review=datetime.now(timezone.utc),
    )
    db.add(card)
    await db.flush()
    await db.refresh(card)
    return card


@router.get("/cards/review/{deck_id}", response_model=List[FlashcardResponse])
async def get_cards_for_review(deck_id: UUID, db: AsyncSession = Depends(get_db)):
    user = await get_default_user(db)
    # Verify deck ownership
    deck_result = await db.execute(
        select(FlashcardDeck).where(
            FlashcardDeck.id == deck_id,
            FlashcardDeck.user_id == user.id,
        )
    )
    deck = deck_result.scalar_one_or_none()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")

    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(Flashcard)
        .where(Flashcard.deck_id == deck_id)
        .where(
            (Flashcard.next_review <= now) | (Flashcard.next_review.is_(None))
        )
        .order_by(Flashcard.next_review)
    )
    return result.scalars().all()


@router.put("/cards/{card_id}/review", response_model=FlashcardResponse)
async def review_flashcard(
    card_id: UUID,
    review_in: FlashcardReview,
    db: AsyncSession = Depends(get_db),
):
    if review_in.quality < 0 or review_in.quality > 5:
        raise HTTPException(status_code=400, detail="Quality must be between 0 and 5")

    result = await db.execute(select(Flashcard).where(Flashcard.id == card_id))
    card = result.scalar_one_or_none()
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    sm2_result = calculate_sm2(
        quality=review_in.quality,
        ease_factor=card.ease_factor,
        interval=card.interval,
        repetitions=card.repetitions,
    )

    card.ease_factor = sm2_result.ease_factor
    card.interval = sm2_result.interval
    card.repetitions = sm2_result.repetitions
    card.last_reviewed = datetime.now(timezone.utc)
    card.next_review = sm2_result.next_review

    await db.flush()
    await db.refresh(card)
    return card


@router.delete("/cards/{card_id}", status_code=204)
async def delete_flashcard(card_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Flashcard).where(Flashcard.id == card_id))
    card = result.scalar_one_or_none()
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    await db.delete(card)
