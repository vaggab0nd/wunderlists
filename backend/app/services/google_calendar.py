"""
Google Calendar integration service for syncing events.

This service handles OAuth authentication and bidirectional sync between
the local calendar_events table and Google Calendar.
"""

import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sqlalchemy.orm import Session

from backend.app.config import get_settings
from backend.app.models.calendar_event import CalendarEvent

logger = logging.getLogger(__name__)

class GoogleCalendarService:
    """Service for Google Calendar integration"""

    SCOPES = ['https://www.googleapis.com/auth/calendar']

    def __init__(self):
        self.settings = get_settings()
        self._credentials: Optional[Credentials] = None
        self._service = None

    def get_oauth_url(self) -> str:
        """
        Generate the OAuth authorization URL for Google Calendar.

        Returns:
            str: The authorization URL where users should be redirected
        """
        from google_auth_oauthlib.flow import Flow

        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.settings.google_client_id,
                    "client_secret": self.settings.google_client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.settings.google_redirect_uri],
                }
            },
            scopes=self.SCOPES,
            redirect_uri=self.settings.google_redirect_uri
        )

        authorization_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )

        return authorization_url

    def exchange_code_for_credentials(self, authorization_code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access/refresh tokens.

        Args:
            authorization_code: The authorization code from OAuth callback

        Returns:
            dict: Credentials data that should be stored securely
        """
        from google_auth_oauthlib.flow import Flow

        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.settings.google_client_id,
                    "client_secret": self.settings.google_client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.settings.google_redirect_uri],
                }
            },
            scopes=self.SCOPES,
            redirect_uri=self.settings.google_redirect_uri
        )

        flow.fetch_token(code=authorization_code)
        credentials = flow.credentials

        return {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }

    def load_credentials(self, credentials_data: Dict[str, Any]) -> bool:
        """
        Load credentials from stored data.

        Args:
            credentials_data: Dictionary with OAuth credentials

        Returns:
            bool: True if credentials loaded successfully
        """
        try:
            self._credentials = Credentials(
                token=credentials_data.get('token'),
                refresh_token=credentials_data.get('refresh_token'),
                token_uri=credentials_data.get('token_uri'),
                client_id=credentials_data.get('client_id'),
                client_secret=credentials_data.get('client_secret'),
                scopes=credentials_data.get('scopes')
            )

            # Refresh if expired
            if self._credentials.expired and self._credentials.refresh_token:
                self._credentials.refresh(Request())

            return True
        except Exception as e:
            logger.error(f"Failed to load credentials: {e}")
            return False

    def get_service(self):
        """Get or create the Google Calendar API service"""
        if not self._service:
            if not self._credentials:
                raise ValueError("Credentials not loaded. Call load_credentials first.")
            self._service = build('calendar', 'v3', credentials=self._credentials)
        return self._service

    def sync_from_google(self, db: Session, calendar_id: str = 'primary') -> Dict[str, int]:
        """
        Sync events from Google Calendar to local database.

        Args:
            db: Database session
            calendar_id: Google Calendar ID (default: 'primary')

        Returns:
            dict: Statistics about synced events (created, updated)
        """
        stats = {'created': 0, 'updated': 0, 'errors': 0}

        try:
            service = self.get_service()

            # Get events from Google Calendar (future events only)
            now = datetime.utcnow().isoformat() + 'Z'
            events_result = service.events().list(
                calendarId=calendar_id,
                timeMin=now,
                maxResults=100,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            google_events = events_result.get('items', [])

            for g_event in google_events:
                try:
                    # Parse Google event
                    external_id = g_event['id']
                    title = g_event.get('summary', 'Untitled Event')
                    description = g_event.get('description', '')
                    location = g_event.get('location', '')

                    # Handle start/end times (datetime or date)
                    start = g_event['start'].get('dateTime', g_event['start'].get('date'))
                    end = g_event['end'].get('dateTime', g_event['end'].get('date'))

                    # Parse to datetime
                    start_time = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    end_time = datetime.fromisoformat(end.replace('Z', '+00:00'))
                    is_all_day = 'date' in g_event['start']

                    # Check if event already exists locally
                    existing = db.query(CalendarEvent).filter(
                        CalendarEvent.external_id == external_id,
                        CalendarEvent.external_source == 'google'
                    ).first()

                    if existing:
                        # Update existing event
                        existing.title = title
                        existing.description = description
                        existing.location = location
                        existing.start_time = start_time
                        existing.end_time = end_time
                        existing.is_all_day = is_all_day
                        stats['updated'] += 1
                    else:
                        # Create new event
                        new_event = CalendarEvent(
                            title=title,
                            description=description,
                            location=location,
                            start_time=start_time,
                            end_time=end_time,
                            is_all_day=is_all_day,
                            external_id=external_id,
                            external_source='google'
                        )
                        db.add(new_event)
                        stats['created'] += 1

                except Exception as e:
                    logger.error(f"Error syncing event {g_event.get('id')}: {e}")
                    stats['errors'] += 1

            db.commit()
            logger.info(f"Sync from Google complete: {stats}")

        except HttpError as e:
            logger.error(f"Google Calendar API error: {e}")
            raise

        return stats

    def sync_to_google(self, db: Session, event_id: int, calendar_id: str = 'primary') -> str:
        """
        Sync a local event to Google Calendar.

        Args:
            db: Database session
            event_id: Local event ID
            calendar_id: Google Calendar ID (default: 'primary')

        Returns:
            str: Google Calendar event ID
        """
        try:
            service = self.get_service()

            # Get local event
            event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
            if not event:
                raise ValueError(f"Event {event_id} not found")

            # Build Google Calendar event
            g_event = {
                'summary': event.title,
                'description': event.description or '',
                'location': event.location or '',
            }

            # Handle all-day vs timed events
            if event.is_all_day:
                g_event['start'] = {'date': event.start_time.date().isoformat()}
                g_event['end'] = {'date': event.end_time.date().isoformat()}
            else:
                g_event['start'] = {'dateTime': event.start_time.isoformat(), 'timeZone': 'UTC'}
                g_event['end'] = {'dateTime': event.end_time.isoformat(), 'timeZone': 'UTC'}

            # Create or update in Google Calendar
            if event.external_id and event.external_source == 'google':
                # Update existing event
                g_event_result = service.events().update(
                    calendarId=calendar_id,
                    eventId=event.external_id,
                    body=g_event
                ).execute()
            else:
                # Create new event
                g_event_result = service.events().insert(
                    calendarId=calendar_id,
                    body=g_event
                ).execute()

                # Update local event with Google ID
                event.external_id = g_event_result['id']
                event.external_source = 'google'
                db.commit()

            return g_event_result['id']

        except HttpError as e:
            logger.error(f"Google Calendar API error: {e}")
            raise
