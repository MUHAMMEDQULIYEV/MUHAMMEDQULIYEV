"""
YouTube transcript extraction service.
"""

import logging
import re
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def extract_video_id(url: str) -> str:
    """Extract YouTube video ID from a URL."""
    patterns = [
        r"(?:v=|\/videos\/|embed\/|youtu\.be\/|\/v\/|\/e\/|watch\?v%3D|watch\?feature=player_embedded&v=|%2Fvideos%2F|embed%2F|youtu\.be%2F|%2Fv%2F)([^#\&\?\n]*)",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract video ID from URL: {url}")


def fetch_transcript(youtube_url: str) -> str:
    """
    Fetch the transcript from a YouTube video URL.
    Returns the full transcript as a single string.
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi

        video_id = extract_video_id(youtube_url)
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([entry["text"] for entry in transcript_list])
        return text
    except ImportError:
        logger.error("youtube-transcript-api not installed.")
        raise RuntimeError("youtube-transcript-api package is required.")
    except Exception as exc:
        logger.error("Failed to fetch transcript for %s: %s", youtube_url, exc)
        raise RuntimeError(f"Could not fetch transcript: {exc}") from exc


def parse_srt(content: str) -> str:
    """Parse an .srt subtitle file and return plain text."""
    lines = content.splitlines()
    text_lines = []
    for line in lines:
        line = line.strip()
        # Skip index numbers and timestamps
        if re.match(r"^\d+$", line):
            continue
        if re.match(r"^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$", line):
            continue
        if line:
            text_lines.append(line)
    return " ".join(text_lines)
