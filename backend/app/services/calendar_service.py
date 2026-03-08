"""
Google Calendar integration service.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from app.config import settings

logger = logging.getLogger(__name__)


def _get_calendar_service():
    """Build and return a Google Calendar service object."""
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        # In production, load credentials from stored token
        # For now, raise an informative error if not configured
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            raise ValueError("Google Calendar credentials not configured.")
        raise NotImplementedError("OAuth2 flow requires user interaction. See README for setup.")
    except ImportError:
        raise RuntimeError("google-api-python-client not installed.")


def sync_calendar_events(token_data: Optional[Dict] = None) -> List[Dict[str, Any]]:
    """
    Sync events from Google Calendar.
    Returns list of upcoming events.
    """
    logger.warning("Google Calendar sync requires OAuth2 setup. Returning empty list.")
    return []


def create_calendar_event(
    title: str,
    description: str,
    start_dt: datetime,
    end_dt: datetime,
    token_data: Optional[Dict] = None,
) -> Dict[str, Any]:
    """
    Create a Google Calendar event from a task.
    """
    logger.warning("Google Calendar event creation requires OAuth2 setup.")
    return {
        "status": "pending_oauth",
        "message": "Google Calendar OAuth2 not configured. Please set up credentials in .env and follow README instructions.",
        "event": {
            "title": title,
            "description": description,
            "start": start_dt.isoformat(),
            "end": end_dt.isoformat(),
        },
    }


def get_upcoming_events(max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Get upcoming Google Calendar events.
    """
    logger.warning("Google Calendar get events requires OAuth2 setup.")
    return []
