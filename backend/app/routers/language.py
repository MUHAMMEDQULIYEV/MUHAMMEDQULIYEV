from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone

from app.database import get_db
from app.models.vocabulary import LanguageVocabulary
from app.schemas.vocabulary import VocabularyResponse, YouTubeExtractRequest, UploadTranscriptRequest
from app.services import youtube_service, nlp_service
from app.utils.helpers import get_default_user

router = APIRouter()


@router.post("/extract-youtube", response_model=List[VocabularyResponse])
async def extract_from_youtube(
    request: YouTubeExtractRequest,
    db: AsyncSession = Depends(get_db),
):
    user = await get_default_user(db)

    try:
        transcript = youtube_service.fetch_transcript(request.url)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    vocab_items = nlp_service.process_text(transcript, request.language)
    saved_vocab = []

    for item in vocab_items[:200]:  # Limit to top 200 words
        vocab = LanguageVocabulary(
            user_id=user.id,
            word=item["word"],
            language=request.language,
            translation="",
            frequency_count=item["frequency_count"],
            source_url=request.url,
            pos=item.get("pos"),
            difficulty=item.get("difficulty", 1),
            learned=False,
            created_at=datetime.now(timezone.utc),
        )
        db.add(vocab)
        saved_vocab.append(vocab)

    await db.flush()
    for v in saved_vocab:
        await db.refresh(v)

    return saved_vocab


@router.post("/extract-upload", response_model=List[VocabularyResponse])
async def extract_from_upload(
    request: UploadTranscriptRequest,
    db: AsyncSession = Depends(get_db),
):
    user = await get_default_user(db)

    content = request.content
    if content.strip().startswith("1\n") or "-->" in content:
        # Likely an SRT file
        content = youtube_service.parse_srt(content)

    vocab_items = nlp_service.process_text(content, request.language)
    saved_vocab = []

    for item in vocab_items[:200]:
        vocab = LanguageVocabulary(
            user_id=user.id,
            word=item["word"],
            language=request.language,
            translation="",
            frequency_count=item["frequency_count"],
            source_url=request.source_url,
            pos=item.get("pos"),
            difficulty=item.get("difficulty", 1),
            learned=False,
            created_at=datetime.now(timezone.utc),
        )
        db.add(vocab)
        saved_vocab.append(vocab)

    await db.flush()
    for v in saved_vocab:
        await db.refresh(v)

    return saved_vocab


@router.get("/vocabulary", response_model=List[VocabularyResponse])
async def list_vocabulary(
    language: Optional[str] = Query(None),
    learned: Optional[bool] = Query(None),
    difficulty: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    user = await get_default_user(db)
    query = select(LanguageVocabulary).where(LanguageVocabulary.user_id == user.id)

    if language:
        query = query.where(LanguageVocabulary.language == language)
    if learned is not None:
        query = query.where(LanguageVocabulary.learned == learned)
    if difficulty is not None:
        query = query.where(LanguageVocabulary.difficulty == difficulty)

    query = query.order_by(LanguageVocabulary.frequency_count.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/analytics")
async def language_analytics(db: AsyncSession = Depends(get_db)):
    user = await get_default_user(db)
    from sqlalchemy import func

    total_result = await db.execute(
        select(func.count(LanguageVocabulary.id)).where(LanguageVocabulary.user_id == user.id)
    )
    learned_result = await db.execute(
        select(func.count(LanguageVocabulary.id))
        .where(LanguageVocabulary.user_id == user.id)
        .where(LanguageVocabulary.learned == True)
    )

    total = total_result.scalar() or 0
    learned = learned_result.scalar() or 0

    by_lang_result = await db.execute(
        select(LanguageVocabulary.language, func.count(LanguageVocabulary.id))
        .where(LanguageVocabulary.user_id == user.id)
        .group_by(LanguageVocabulary.language)
    )
    by_language = {lang: count for lang, count in by_lang_result.all()}

    return {
        "total_words": total,
        "learned_words": learned,
        "learning_rate": round(learned / total * 100, 1) if total > 0 else 0.0,
        "by_language": by_language,
    }


@router.post("/vocabulary/{vocab_id}/mark-learned", response_model=VocabularyResponse)
async def mark_vocabulary_learned(vocab_id: UUID, db: AsyncSession = Depends(get_db)):
    user = await get_default_user(db)
    result = await db.execute(
        select(LanguageVocabulary).where(
            LanguageVocabulary.id == vocab_id,
            LanguageVocabulary.user_id == user.id,
        )
    )
    vocab = result.scalar_one_or_none()
    if not vocab:
        raise HTTPException(status_code=404, detail="Vocabulary item not found")

    vocab.learned = True
    vocab.date_learned = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(vocab)
    return vocab
