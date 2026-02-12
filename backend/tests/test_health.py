"""
Tests for health check and ping endpoints
"""
import pytest
from fastapi import status


@pytest.mark.api
class TestPingEndpoint:
    """Tests for GET /api/ping endpoint"""

    def test_ping(self, client):
        """Test ping returns pong"""
        response = client.get("/api/ping")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "ok"
        assert data["message"] == "pong"
        assert data["service"] == "wunderlists"
        assert "timestamp" in data


@pytest.mark.api
class TestHealthEndpoint:
    """Tests for GET /health and /api/health endpoints"""

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/api/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["service"] == "wunderlists"
        assert data["version"] == "1.0.0"
        assert "database" in data
        assert "environment" in data

    def test_health_check_alternate_path(self, client):
        """Test health check on /health path"""
        response = client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["service"] == "wunderlists"
