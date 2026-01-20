"""
Routes for Google Calendar synchronization.

Provides endpoints for:
- OAuth flow (connect to Google Calendar)
- Manual sync (pull events from Google)
- Auto-sync when creating/updating local events
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Dict
import json
import logging

from backend.app.database import get_db
from backend.app.services.google_calendar import GoogleCalendarService
from backend.app.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/calendar-sync", tags=["calendar-sync"])

# In-memory storage for credentials (in production, store in database)
_credentials_store: Dict = {}

@router.get("/connect")
def connect_google_calendar():
    """
    Initiate Google Calendar OAuth flow.

    Returns the authorization URL where the user should be redirected
    to grant calendar access.
    """
    try:
        service = GoogleCalendarService()
        auth_url = service.get_oauth_url()
        return {
            "authorization_url": auth_url,
            "message": "Visit this URL to authorize Google Calendar access"
        }
    except Exception as e:
        logger.error(f"Error generating OAuth URL: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate OAuth URL: {str(e)}")

@router.get("/oauth-callback")
def oauth_callback(code: str = Query(..., description="Authorization code from Google")):
    """
    OAuth callback endpoint.

    Google redirects here after user authorizes access.
    Exchanges the authorization code for credentials and stores them.
    """
    try:
        service = GoogleCalendarService()
        credentials_data = service.exchange_code_for_credentials(code)

        # Store credentials (in production, store in database)
        _credentials_store['google_calendar'] = credentials_data

        logger.info("Google Calendar connected successfully")

        return {
            "status": "success",
            "message": "Google Calendar connected successfully! You can now sync your events."
        }
    except Exception as e:
        logger.error(f"OAuth callback error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to complete OAuth: {str(e)}")

@router.get("/status")
def get_sync_status():
    """
    Check if Google Calendar is connected.

    Returns connection status and stored credentials info.
    """
    is_connected = 'google_calendar' in _credentials_store

    return {
        "connected": is_connected,
        "message": "Google Calendar is connected" if is_connected else "Google Calendar not connected. Use /connect endpoint."
    }

@router.post("/sync-from-google")
def sync_from_google(db: Session = Depends(get_db)):
    """
    Manually trigger sync from Google Calendar to local database.

    Pulls upcoming events from Google Calendar and creates/updates
    local calendar_events records.
    """
    if 'google_calendar' not in _credentials_store:
        raise HTTPException(
            status_code=400,
            detail="Google Calendar not connected. Use /connect endpoint first."
        )

    try:
        service = GoogleCalendarService()
        service.load_credentials(_credentials_store['google_calendar'])

        stats = service.sync_from_google(db)

        return {
            "status": "success",
            "message": f"Synced from Google Calendar",
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Sync from Google error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

@router.post("/sync-to-google/{event_id}")
def sync_to_google(event_id: int, db: Session = Depends(get_db)):
    """
    Sync a specific local event to Google Calendar.

    Args:
        event_id: The local calendar_events.id to sync

    Creates or updates the event in Google Calendar.
    """
    if 'google_calendar' not in _credentials_store:
        raise HTTPException(
            status_code=400,
            detail="Google Calendar not connected. Use /connect endpoint first."
        )

    try:
        service = GoogleCalendarService()
        service.load_credentials(_credentials_store['google_calendar'])

        google_event_id = service.sync_to_google(db, event_id)

        return {
            "status": "success",
            "message": f"Event synced to Google Calendar",
            "google_event_id": google_event_id
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Sync to Google error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

@router.delete("/disconnect")
def disconnect_google_calendar():
    """
    Disconnect Google Calendar.

    Removes stored credentials.
    """
    if 'google_calendar' in _credentials_store:
        del _credentials_store['google_calendar']

    return {
        "status": "success",
        "message": "Google Calendar disconnected"
    }
