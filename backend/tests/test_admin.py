"""
Tests for Admin API endpoints
Tests database stats and clear-all-data operations
"""
import pytest
from fastapi import status


@pytest.mark.api
class TestDatabaseStats:
    """Tests for GET /api/admin/stats endpoint"""

    def test_get_stats_empty_database(self, client):
        """Test stats with empty database"""
        response = client.get("/api/admin/stats")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "tasks" in data
        assert "lists" in data
        assert "calendar_events" in data
        assert "locations" in data
        assert data["tasks"]["total"] == 0
        assert data["tasks"]["completed"] == 0
        assert data["tasks"]["incomplete"] == 0

    def test_get_stats_with_data(self, client, sample_task, sample_completed_task, sample_list, sample_calendar_event, sample_location):
        """Test stats with data in database"""
        response = client.get("/api/admin/stats")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["tasks"]["total"] == 2
        assert data["tasks"]["completed"] == 1
        assert data["tasks"]["incomplete"] == 1
        assert data["lists"] >= 1
        assert data["calendar_events"] >= 1
        assert data["locations"] >= 1


@pytest.mark.api
class TestClearAllData:
    """Tests for DELETE /api/admin/clear-all-data endpoint"""

    def test_clear_data_without_confirmation_fails(self, client):
        """Test that clearing data without confirmation fails"""
        response = client.delete("/api/admin/clear-all-data")

        assert response.status_code == 400
        assert "confirm" in response.json()["detail"].lower()

    def test_clear_data_with_wrong_confirmation_fails(self, client):
        """Test that wrong confirmation string fails"""
        response = client.delete("/api/admin/clear-all-data?confirm=DELETE")

        assert response.status_code == 400

    def test_clear_data_with_correct_confirmation(self, client, sample_task, sample_list, sample_calendar_event, sample_location):
        """Test clearing all data with correct confirmation"""
        # Verify data exists
        stats = client.get("/api/admin/stats").json()
        assert stats["tasks"]["total"] > 0

        response = client.delete(
            "/api/admin/clear-all-data?confirm=YES_DELETE_EVERYTHING"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
        assert data["deleted"]["total"] > 0

        # Verify data is gone
        stats_after = client.get("/api/admin/stats").json()
        assert stats_after["tasks"]["total"] == 0
        assert stats_after["lists"] == 0
        assert stats_after["calendar_events"] == 0
        assert stats_after["locations"] == 0

    def test_clear_data_on_empty_database(self, client):
        """Test clearing an already empty database"""
        response = client.delete(
            "/api/admin/clear-all-data?confirm=YES_DELETE_EVERYTHING"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["deleted"]["total"] == 0
