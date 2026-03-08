"""
NLP service for English (spaCy) and Korean (KoNLPy) text processing.
"""

import logging
from typing import List, Dict, Any, Optional
from collections import Counter

logger = logging.getLogger(__name__)

# Fallback English stopwords (used if NLTK is unavailable)
_FALLBACK_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "it", "this", "that", "was", "are",
    "be", "been", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "shall", "can", "not", "no", "nor",
    "so", "yet", "both", "either", "neither", "whether", "as", "if", "than",
    "because", "since", "while", "after", "before", "though", "although",
    "however", "therefore", "thus", "hence", "he", "she", "they", "we",
    "you", "i", "me", "him", "her", "them", "us", "my", "your", "his",
    "its", "our", "their", "what", "which", "who", "whom", "whose", "when",
    "where", "why", "how", "all", "each", "every", "any", "some", "more",
    "most", "other", "into", "up", "about", "through", "during", "then",
    "now", "just", "also", "only", "even", "still", "well", "much", "many",
    "such", "own", "same", "too", "very", "s", "t", "re", "ll", "ve", "d",
}


def _get_english_stopwords() -> set:
    """Return NLTK stopwords if available, otherwise use fallback set."""
    try:
        from nltk.corpus import stopwords
        return set(stopwords.words("english"))
    except Exception:
        return _FALLBACK_STOPWORDS


ENGLISH_STOPWORDS = _get_english_stopwords()


def _get_difficulty(rank: int, total: int) -> int:
    """Compute difficulty score 1-5 based on frequency rank."""
    if total == 0:
        return 3
    pct = rank / total
    if pct <= 0.1:
        return 1
    elif pct <= 0.3:
        return 2
    elif pct <= 0.6:
        return 3
    elif pct <= 0.85:
        return 4
    else:
        return 5


def process_english(text: str) -> List[Dict[str, Any]]:
    """
    Process English text using spaCy.
    Returns list of vocabulary items with word, pos, frequency, difficulty.
    """
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
    except Exception as exc:
        logger.warning("spaCy not available, falling back to basic tokenization: %s", exc)
        return _basic_english_process(text)

    doc = nlp(text)
    word_data: Dict[str, Dict] = {}

    for token in doc:
        lemma = token.lemma_.lower()
        if (
            token.is_alpha
            and not token.is_stop
            and len(lemma) > 2
            and lemma not in ENGLISH_STOPWORDS
            and token.pos_ in ("NOUN", "VERB", "ADJ", "ADV")
        ):
            if lemma not in word_data:
                word_data[lemma] = {"word": lemma, "pos": token.pos_, "frequency": 0}
            word_data[lemma]["frequency"] += 1

    # Sort by frequency descending, take top 500
    sorted_words = sorted(word_data.values(), key=lambda x: x["frequency"], reverse=True)[:500]
    total = len(sorted_words)

    return [
        {
            "word": item["word"],
            "pos": item["pos"],
            "frequency_count": item["frequency"],
            "difficulty": _get_difficulty(i, total),
        }
        for i, item in enumerate(sorted_words)
    ]


def _basic_english_process(text: str) -> List[Dict[str, Any]]:
    """Fallback basic English processing without spaCy."""
    import re
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    filtered = [w for w in words if w not in ENGLISH_STOPWORDS]
    counter = Counter(filtered)
    sorted_words = counter.most_common(500)
    total = len(sorted_words)

    return [
        {
            "word": word,
            "pos": "NOUN",
            "frequency_count": freq,
            "difficulty": _get_difficulty(i, total),
        }
        for i, (word, freq) in enumerate(sorted_words)
    ]


def process_korean(text: str) -> List[Dict[str, Any]]:
    """
    Process Korean text using KoNLPy Okt.
    Returns list of vocabulary items.
    """
    try:
        from konlpy.tag import Okt
        okt = Okt()
        morphs = okt.pos(text, norm=True, stem=True)

        word_data: Dict[str, Dict] = {}
        for word, pos in morphs:
            if (
                pos in ("Noun", "Verb", "Adjective")
                and len(word) >= 2
                and not word.isdigit()
            ):
                if word not in word_data:
                    word_data[word] = {"word": word, "pos": pos, "frequency": 0}
                word_data[word]["frequency"] += 1

        sorted_words = sorted(word_data.values(), key=lambda x: x["frequency"], reverse=True)[:500]
        total = len(sorted_words)

        return [
            {
                "word": item["word"],
                "pos": item["pos"],
                "frequency_count": item["frequency"],
                "difficulty": _get_difficulty(i, total),
            }
            for i, item in enumerate(sorted_words)
        ]
    except Exception as exc:
        logger.warning("KoNLPy not available: %s", exc)
        return _basic_korean_process(text)


def _basic_korean_process(text: str) -> List[Dict[str, Any]]:
    """Fallback basic Korean processing without KoNLPy."""
    import re
    # Match Korean characters (Hangul)
    words = re.findall(r"[\uAC00-\uD7A3]{2,}", text)
    counter = Counter(words)
    sorted_words = counter.most_common(500)
    total = len(sorted_words)

    return [
        {
            "word": word,
            "pos": "Noun",
            "frequency_count": freq,
            "difficulty": _get_difficulty(i, total),
        }
        for i, (word, freq) in enumerate(sorted_words)
    ]


def process_text(text: str, language: str = "english") -> List[Dict[str, Any]]:
    """
    Process text and extract vocabulary based on language.
    """
    if language.lower() == "korean":
        return process_korean(text)
    return process_english(text)
