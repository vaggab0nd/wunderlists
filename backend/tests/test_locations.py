"""
Comprehensive tests for Locations API endpoints
Tests all CRUD operations, filtering, validation, and edge cases
"""
import pytest
from fastapi import status


@pytest.mark.api
class TestLocationCreation:
    """Tests for POST /api/locations/ endpoint"""

    def test_create_location_minimal(self, client):
        """Test creating a location with required fields"""
        response = client.post("/api/locations/", json={
            "name": "Home",
            "city": "Dublin",
            "country": "Ireland"
        })

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Home"
        assert data["city"] == "Dublin"
        assert data["country"] == "Ireland"
        assert data["show_in_dashboard"] is True  # Default
        assert data["is_favorite"] is False  # Default
        assert data["id"] is not None

    def test_create_location_full_details(self, client):
        """Test creating a location with all fields"""
        response = client.post("/api/locations/", json={
            "name": "Office",
            "city": "London",
            "country": "UK",
            "latitude": 51.5074,
            "longitude": -0.1278,
            "is_favorite": True,
            "show_in_dashboard": False
        })

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Office"
        assert data["latitude"] == 51.5074
        assert data["longitude"] == -0.1278
        assert data["is_favorite"] is True
        assert data["show_in_dashboard"] is False

    def test_create_location_missing_name_fails(self, client):
        """Test that missing name fails validation"""
        response = client.post("/api/locations/", json={
            "city": "Dublin",
            "country": "Ireland"
        })

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_location_missing_city_fails(self, client):
        """Test that missing city fails validation"""
        response = client.post("/api/locations/", json={
            "name": "Home",
            "country": "Ireland"
        })

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_location_missing_country_fails(self, client):
        """Test that missing country fails validation"""
        response = client.post("/api/locations/", json={
            "name": "Home",
            "city": "Dublin"
        })

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_location_invalid_latitude_fails(self, client):
        """Test that latitude outside [-90, 90] fails"""
        response = client.post("/api/locations/", json={
            "name": "Invalid",
            "city": "Test",
            "country": "Test",
            "latitude": 91.0
        })

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_location_invalid_longitude_fails(self, client):
        """Test that longitude outside [-180, 180] fails"""
        response = client.post("/api/locations/", json={
            "name": "Invalid",
            "city": "Test",
            "country": "Test",
            "longitude": 181.0
        })

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_location_boundary_coordinates(self, client):
        """Test that boundary lat/lon values are accepted"""
        response = client.post("/api/locations/", json={
            "name": "Boundary",
            "city": "Test",
            "country": "Test",
            "latitude": 90.0,
            "longitude": -180.0
        })

        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.api
class TestLocationRetrieval:
    """Tests for GET /api/locations/ and GET /api/locations/{id} endpoints"""

    def test_get_all_locations_empty(self, client):
        """Test getting locations when database is empty"""
        response = client.get("/api/locations/")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_get_all_locations(self, client, sample_location):
        """Test getting all locations"""
        response = client.get("/api/locations/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1

    def test_get_location_by_id(self, client, sample_location):
        """Test getting a specific location by ID"""
        response = client.get(f"/api/locations/{sample_location.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == sample_location.id
        assert data["name"] == sample_location.name
        assert data["city"] == sample_location.city

    def test_get_nonexistent_location_returns_404(self, client):
        """Test that getting a non-existent location returns 404"""
        response = client.get("/api/locations/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Location not found"

    def test_filter_dashboard_locations_only(self, client):
        """Test filtering locations by show_in_dashboard"""
        # Create dashboard location
        client.post("/api/locations/", json={
            "name": "Dashboard Loc",
            "city": "Dublin",
            "country": "Ireland",
            "show_in_dashboard": True
        })
        # Create non-dashboard location
        client.post("/api/locations/", json={
            "name": "Hidden Loc",
            "city": "London",
            "country": "UK",
            "show_in_dashboard": False
        })

        response = client.get("/api/locations/?show_in_dashboard_only=true")
        names = [l["name"] for l in response.json()]
        assert "Dashboard Loc" in names
        assert "Hidden Loc" not in names

    def test_get_locations_with_pagination(self, client):
        """Test pagination"""
        for i in range(4):
            client.post("/api/locations/", json={
                "name": f"Location {i}",
                "city": f"City {i}",
                "country": "Test"
            })

        response = client.get("/api/locations/?skip=0&limit=2")
        assert len(response.json()) == 2

        response = client.get("/api/locations/?skip=2&limit=2")
        assert len(response.json()) == 2


@pytest.mark.api
class TestLocationUpdate:
    """Tests for PUT /api/locations/{id} endpoint"""

    def test_update_location_name(self, client, sample_location):
        """Test updating location name"""
        response = client.put(f"/api/locations/{sample_location.id}", json={
            "name": "Updated Name"
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == "Updated Name"

    def test_update_location_coordinates(self, client, sample_location):
        """Test updating coordinates"""
        response = client.put(f"/api/locations/{sample_location.id}", json={
            "latitude": 48.8566,
            "longitude": 2.3522
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["latitude"] == 48.8566
        assert response.json()["longitude"] == 2.3522

    def test_toggle_dashboard_visibility(self, client, sample_location):
        """Test toggling show_in_dashboard"""
        response = client.put(f"/api/locations/{sample_location.id}", json={
            "show_in_dashboard": False
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["show_in_dashboard"] is False

    def test_toggle_favorite(self, client, sample_location):
        """Test toggling is_favorite"""
        response = client.put(f"/api/locations/{sample_location.id}", json={
            "is_favorite": True
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["is_favorite"] is True

    def test_update_nonexistent_location_returns_404(self, client):
        """Test updating a non-existent location"""
        response = client.put("/api/locations/99999", json={
            "name": "Should fail"
        })

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_partial_update_preserves_other_fields(self, client, sample_location):
        """Test that partial updates preserve unchanged fields"""
        original_city = sample_location.city

        response = client.put(f"/api/locations/{sample_location.id}", json={
            "name": "New Name"
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["city"] == original_city


@pytest.mark.api
class TestLocationDeletion:
    """Tests for DELETE /api/locations/{id} endpoint"""

    def test_delete_location(self, client, sample_location):
        """Test deleting a location"""
        loc_id = sample_location.id

        response = client.delete(f"/api/locations/{loc_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deletion
        get_response = client.get(f"/api/locations/{loc_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_nonexistent_location_returns_404(self, client):
        """Test deleting non-existent location returns 404"""
        response = client.delete("/api/locations/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
