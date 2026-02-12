"""
Tests for Weather API routes and Weather Alerts routes.
Weather endpoints use external APIs, so we test the route logic and error handling.
"""
import pytest
from fastapi import status


@pytest.mark.api
class TestWeatherCurrentEndpoint:
    """Tests for GET /api/weather/current/{location_id} endpoint"""

    def test_weather_nonexistent_location_returns_404(self, client):
        """Test that requesting weather for non-existent location returns 404"""
        response = client.get("/api/weather/current/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Location not found"

    def test_weather_for_location(self, client, sample_location):
        """Test fetching weather for a valid location (returns data or error from API)"""
        response = client.get(f"/api/weather/current/{sample_location.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "location" in data
        assert data["location"]["id"] == sample_location.id
        assert "weather" in data


@pytest.mark.api
class TestWeatherDashboardEndpoint:
    """Tests for GET /api/weather/dashboard endpoint"""

    def test_dashboard_weather_empty(self, client):
        """Test dashboard weather with no locations"""
        response = client.get("/api/weather/dashboard")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_dashboard_weather_with_locations(self, client, sample_location):
        """Test dashboard weather with dashboard-visible locations"""
        response = client.get("/api/weather/dashboard")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # sample_location has show_in_dashboard=True
        assert len(data) >= 1
        assert data[0]["location"]["id"] == sample_location.id


@pytest.mark.api
class TestWeatherForecastEndpoint:
    """Tests for GET /api/weather/forecast/{location_id} endpoint"""

    def test_forecast_nonexistent_location_returns_404(self, client):
        """Test forecast for non-existent location returns 404"""
        response = client.get("/api/weather/forecast/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_forecast_for_location(self, client, sample_location):
        """Test fetching forecast for a valid location"""
        response = client.get(f"/api/weather/forecast/{sample_location.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "location" in data
        assert "forecast" in data


@pytest.mark.api
class TestWeatherAlertsTravel:
    """Tests for GET /api/weather/alerts/travel endpoint"""

    def test_travel_alerts_empty(self, client):
        """Test travel alerts when no upcoming events with locations"""
        response = client.get("/api/weather/alerts/travel")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_travel_alerts_days_ahead_param(self, client):
        """Test days_ahead parameter validation"""
        # Valid range
        response = client.get("/api/weather/alerts/travel?days_ahead=1")
        assert response.status_code == status.HTTP_200_OK

        response = client.get("/api/weather/alerts/travel?days_ahead=14")
        assert response.status_code == status.HTTP_200_OK

        # Out of range
        response = client.get("/api/weather/alerts/travel?days_ahead=0")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        response = client.get("/api/weather/alerts/travel?days_ahead=15")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.api
class TestOpenMeteoWeatherAlerts:
    """Tests for GET /api/weather/alerts endpoint (Open-Meteo based)"""

    def test_weather_alerts_empty(self, client):
        """Test weather alerts with no travel day tasks"""
        response = client.get("/api/weather/alerts")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "alerts" in data
        assert "summary" in data
        assert data["summary"]["travel_days_checked"] == 0

    def test_weather_alerts_days_ahead_param(self, client):
        """Test days_ahead parameter"""
        response = client.get("/api/weather/alerts?days_ahead=3")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "summary" in data
        assert "date_range" in data["summary"]


@pytest.mark.api
class TestOpenMeteoWeatherRefresh:
    """Tests for GET /api/weather/refresh endpoint"""

    def test_refresh_endpoint(self, client):
        """Test refresh endpoint returns data with metadata"""
        response = client.get("/api/weather/refresh")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "alerts" in data
        assert "summary" in data
        assert "refresh_metadata" in data
        assert data["refresh_metadata"]["data_source"] == "Open-Meteo API (free)"


@pytest.mark.api
class TestOpenMeteoWeatherTest:
    """Tests for GET /api/weather/test endpoint"""

    def test_weather_test_endpoint(self, client):
        """Test the weather service test endpoint"""
        response = client.get("/api/weather/test")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        assert "test_date" in data
        assert "locations" in data
        assert "Dublin" in data["locations"]
        assert "Île de Ré" in data["locations"]


@pytest.mark.api
class TestOpenMeteoCurrentWeather:
    """Tests for GET /api/weather/current endpoint (Open-Meteo)"""

    def test_current_weather_endpoint(self, client):
        """Test current weather for dashboard locations"""
        response = client.get("/api/weather/current")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "locations" in data
        assert "updated_at" in data
        assert data["data_source"] == "Open-Meteo"


@pytest.mark.api
class TestOpenMeteoMonitoredLocations:
    """Tests for GET /api/weather/locations endpoint"""

    def test_monitored_locations_endpoint(self, client):
        """Test getting the hardcoded monitored locations"""
        response = client.get("/api/weather/locations")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "locations" in data
        assert len(data["locations"]) == 2

        location_keys = [l["key"] for l in data["locations"]]
        assert "Dublin" in location_keys
        assert "Île de Ré" in location_keys

        assert "data_source" in data
        assert data["data_source"]["api_key_required"] is False
