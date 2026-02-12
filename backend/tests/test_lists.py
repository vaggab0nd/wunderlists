"""
Comprehensive tests for Lists API endpoints
Tests all CRUD operations, filtering, validation, and edge cases
"""
import pytest
from fastapi import status


@pytest.mark.api
class TestListCreation:
    """Tests for POST /api/lists/ endpoint"""

    def test_create_list_minimal(self, client):
        """Test creating a list with only required fields"""
        response = client.post("/api/lists/", json={
            "name": "My List"
        })

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "My List"
        assert data["color"] == "#3B82F6"  # Default color
        assert data["is_archived"] is False
        assert data["id"] is not None
        assert data["created_at"] is not None

    def test_create_list_full_details(self, client):
        """Test creating a list with all fields"""
        response = client.post("/api/lists/", json={
            "name": "Work Tasks",
            "description": "All work-related tasks",
            "color": "#FF5733",
            "icon": "💼"
        })

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Work Tasks"
        assert data["description"] == "All work-related tasks"
        assert data["color"] == "#FF5733"
        assert data["icon"] == "💼"

    def test_create_list_empty_name_fails(self, client):
        """Test that empty name fails validation"""
        response = client.post("/api/lists/", json={
            "name": ""
        })

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_list_missing_name_fails(self, client):
        """Test that missing name fails validation"""
        response = client.post("/api/lists/", json={
            "description": "No name list"
        })

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_list_invalid_color_fails(self, client):
        """Test that invalid hex color is rejected"""
        response = client.post("/api/lists/", json={
            "name": "Bad Color List",
            "color": "red"
        })

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_list_valid_hex_colors(self, client):
        """Test that valid hex colors are accepted"""
        for color in ["#000000", "#FFFFFF", "#ff5733", "#aaBBcc"]:
            response = client.post("/api/lists/", json={
                "name": f"List with {color}",
                "color": color
            })
            assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.api
class TestListRetrieval:
    """Tests for GET /api/lists/ and GET /api/lists/{id} endpoints"""

    def test_get_all_lists_empty(self, client):
        """Test getting lists when database is empty"""
        response = client.get("/api/lists/")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_get_all_lists(self, client, sample_list):
        """Test getting all lists"""
        response = client.get("/api/lists/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1
        assert any(l["id"] == sample_list.id for l in data)

    def test_get_list_by_id(self, client, sample_list):
        """Test getting a specific list by ID"""
        response = client.get(f"/api/lists/{sample_list.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == sample_list.id
        assert data["name"] == sample_list.name
        assert data["color"] == sample_list.color

    def test_get_nonexistent_list_returns_404(self, client):
        """Test that getting a non-existent list returns 404"""
        response = client.get("/api/lists/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "List not found"

    def test_get_lists_with_pagination(self, client):
        """Test pagination with skip and limit parameters"""
        # Create multiple lists
        for i in range(5):
            client.post("/api/lists/", json={"name": f"List {i}"})

        response = client.get("/api/lists/?skip=0&limit=2")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 2

        response = client.get("/api/lists/?skip=3&limit=10")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 2

    def test_get_lists_excludes_archived_by_default(self, client):
        """Test that archived lists are excluded by default"""
        # Create a list and archive it
        resp = client.post("/api/lists/", json={"name": "Archived List"})
        list_id = resp.json()["id"]
        client.put(f"/api/lists/{list_id}", json={"is_archived": True})

        client.post("/api/lists/", json={"name": "Active List"})

        response = client.get("/api/lists/")
        names = [l["name"] for l in response.json()]
        assert "Archived List" not in names
        assert "Active List" in names

    def test_get_lists_include_archived(self, client):
        """Test include_archived parameter"""
        resp = client.post("/api/lists/", json={"name": "Archived List"})
        list_id = resp.json()["id"]
        client.put(f"/api/lists/{list_id}", json={"is_archived": True})

        response = client.get("/api/lists/?include_archived=true")
        names = [l["name"] for l in response.json()]
        assert "Archived List" in names


@pytest.mark.api
class TestListUpdate:
    """Tests for PUT /api/lists/{id} endpoint"""

    def test_update_list_name(self, client, sample_list):
        """Test updating list name"""
        response = client.put(f"/api/lists/{sample_list.id}", json={
            "name": "Updated Name"
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == "Updated Name"

    def test_update_list_color(self, client, sample_list):
        """Test updating list color"""
        response = client.put(f"/api/lists/{sample_list.id}", json={
            "color": "#00FF00"
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["color"] == "#00FF00"

    def test_update_list_description(self, client, sample_list):
        """Test updating list description"""
        response = client.put(f"/api/lists/{sample_list.id}", json={
            "description": "Updated description"
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["description"] == "Updated description"

    def test_update_list_icon(self, client, sample_list):
        """Test updating list icon"""
        response = client.put(f"/api/lists/{sample_list.id}", json={
            "icon": "🎯"
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["icon"] == "🎯"

    def test_archive_list(self, client, sample_list):
        """Test archiving a list"""
        response = client.put(f"/api/lists/{sample_list.id}", json={
            "is_archived": True
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["is_archived"] is True

    def test_unarchive_list(self, client, sample_list):
        """Test unarchiving a list"""
        # First archive
        client.put(f"/api/lists/{sample_list.id}", json={"is_archived": True})

        # Then unarchive
        response = client.put(f"/api/lists/{sample_list.id}", json={
            "is_archived": False
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["is_archived"] is False

    def test_update_nonexistent_list_returns_404(self, client):
        """Test updating a non-existent list returns 404"""
        response = client.put("/api/lists/99999", json={
            "name": "Should fail"
        })

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_partial_update_preserves_other_fields(self, client, sample_list):
        """Test that partial updates don't affect other fields"""
        original_color = sample_list.color

        response = client.put(f"/api/lists/{sample_list.id}", json={
            "description": "Only updating description"
        })

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["color"] == original_color
        assert data["description"] == "Only updating description"


@pytest.mark.api
class TestListDeletion:
    """Tests for DELETE /api/lists/{id} endpoint"""

    def test_delete_list(self, client, sample_list):
        """Test deleting a list"""
        response = client.delete(f"/api/lists/{sample_list.id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify list is deleted
        get_response = client.get(f"/api/lists/{sample_list.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_nonexistent_list_returns_404(self, client):
        """Test deleting a non-existent list returns 404"""
        response = client.delete("/api/lists/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_list_cascades_to_tasks(self, client, sample_list, sample_task):
        """Test that deleting a list also deletes its tasks"""
        task_id = sample_task.id
        assert sample_task.list_id == sample_list.id

        response = client.delete(f"/api/lists/{sample_list.id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Task should be gone too (cascade delete)
        task_response = client.get(f"/api/tasks/{task_id}")
        assert task_response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.api
class TestListEdgeCases:
    """Tests for edge cases and special scenarios"""

    def test_list_with_max_length_name(self, client):
        """Test creating a list with 255-char name"""
        long_name = "A" * 255
        response = client.post("/api/lists/", json={"name": long_name})

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["name"] == long_name

    def test_list_with_name_exceeding_max_fails(self, client):
        """Test that name exceeding 255 characters fails"""
        response = client.post("/api/lists/", json={"name": "A" * 256})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_list_with_emoji_icon(self, client):
        """Test creating a list with emoji icon"""
        response = client.post("/api/lists/", json={
            "name": "Emoji List",
            "icon": "🚀"
        })

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["icon"] == "🚀"

    def test_create_multiple_lists(self, client):
        """Test creating multiple lists"""
        for i in range(3):
            resp = client.post("/api/lists/", json={"name": f"List {i}"})
            assert resp.status_code == status.HTTP_201_CREATED

        response = client.get("/api/lists/")
        assert len(response.json()) == 3
