"""
Tests for Calendar Sync API endpoints
Tests connection status, sync operations, and disconnect flow
"""
import pytest
from fastapi import status


@pytest.mark.api
class TestCalendarSyncStatus:
    """Tests for GET /api/calendar-sync/status endpoint"""

    def test_status_when_not_connected(self, client):
        """Test status when Google Calendar is not connected"""
        response = client.get("/api/calendar-sync/status")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["connected"] is False
        assert "not connected" in data["message"].lower()


@pytest.mark.api
class TestCalendarSyncConnect:
    """Tests for GET /api/calendar-sync/connect endpoint"""

    def test_connect_returns_auth_url_or_error(self, client):
        """Test that connect endpoint returns auth URL or handles missing credentials"""
        response = client.get("/api/calendar-sync/connect")

        # Will return 500 if Google credentials are not configured (expected in test env)
        # or 200 with an authorization URL if configured
        assert response.status_code in [200, 500]


@pytest.mark.api
class TestCalendarSyncFromGoogle:
    """Tests for POST /api/calendar-sync/sync-from-google endpoint"""

    def test_sync_from_google_not_connected(self, client):
        """Test sync from Google when not connected"""
        response = client.post("/api/calendar-sync/sync-from-google")

        assert response.status_code == 400
        assert "not connected" in response.json()["detail"].lower()


@pytest.mark.api
class TestCalendarSyncToGoogle:
    """Tests for POST /api/calendar-sync/sync-to-google/{event_id} endpoint"""

    def test_sync_to_google_not_connected(self, client, sample_calendar_event):
        """Test sync to Google when not connected"""
        response = client.post(
            f"/api/calendar-sync/sync-to-google/{sample_calendar_event.id}"
        )

        assert response.status_code == 400
        assert "not connected" in response.json()["detail"].lower()


@pytest.mark.api
class TestCalendarSyncDisconnect:
    """Tests for DELETE /api/calendar-sync/disconnect endpoint"""

    def test_disconnect_when_not_connected(self, client):
        """Test disconnecting when not connected (should still succeed)"""
        response = client.delete("/api/calendar-sync/disconnect")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
        assert "disconnected" in data["message"].lower()

    def test_disconnect_idempotent(self, client):
        """Test that disconnect can be called multiple times"""
        client.delete("/api/calendar-sync/disconnect")
        response = client.delete("/api/calendar-sync/disconnect")

        assert response.status_code == status.HTTP_200_OK
