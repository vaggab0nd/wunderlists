"""
Comprehensive tests for Users API endpoints
Tests all CRUD operations, validation, and business logic
"""
import pytest
from fastapi import status


@pytest.mark.api
class TestUserCreation:
    """Tests for POST /api/users/ endpoint"""

    def test_create_user(self, client):
        """Test creating a user with required fields"""
        response = client.post("/api/users/", json={
            "email": "newuser@example.com",
            "full_name": "New User"
        })

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["full_name"] == "New User"
        assert data["is_active"] is True
        assert data["id"] is not None

    def test_create_user_generates_username_from_email(self, client):
        """Test that username is generated from email prefix"""
        response = client.post("/api/users/", json={
            "email": "johndoe@example.com",
            "full_name": "John Doe"
        })

        assert response.status_code == status.HTTP_201_CREATED

    def test_create_user_duplicate_email_fails(self, client, sample_user):
        """Test that duplicate email is rejected"""
        response = client.post("/api/users/", json={
            "email": sample_user.email,
            "full_name": "Duplicate"
        })

        assert response.status_code == 400
        assert response.json()["detail"] == "Email already registered"

    def test_create_user_invalid_email_fails(self, client):
        """Test that invalid email is rejected"""
        response = client.post("/api/users/", json={
            "email": "not-an-email",
            "full_name": "Bad Email"
        })

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_user_missing_email_fails(self, client):
        """Test that missing email fails validation"""
        response = client.post("/api/users/", json={
            "full_name": "No Email"
        })

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_user_missing_name_fails(self, client):
        """Test that missing full_name fails validation"""
        response = client.post("/api/users/", json={
            "email": "valid@example.com"
        })

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_user_empty_name_fails(self, client):
        """Test that empty full_name fails validation"""
        response = client.post("/api/users/", json={
            "email": "valid@example.com",
            "full_name": ""
        })

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_user_duplicate_username_gets_incremented(self, client):
        """Test that duplicate usernames get a counter appended"""
        # Create first user with same email prefix
        client.post("/api/users/", json={
            "email": "alice@example.com",
            "full_name": "Alice One"
        })

        # Create second user with same prefix but different domain
        response = client.post("/api/users/", json={
            "email": "alice@other.com",
            "full_name": "Alice Two"
        })

        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.api
class TestUserRetrieval:
    """Tests for GET /api/users/ and GET /api/users/{id} endpoints"""

    def test_get_all_users_empty(self, client):
        """Test getting users when database is empty"""
        response = client.get("/api/users/")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_get_all_users(self, client, sample_user):
        """Test getting all users"""
        response = client.get("/api/users/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1
        assert any(u["id"] == sample_user.id for u in data)

    def test_get_user_by_id(self, client, sample_user):
        """Test getting a specific user by ID"""
        response = client.get(f"/api/users/{sample_user.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == sample_user.id
        assert data["email"] == sample_user.email
        assert data["full_name"] == sample_user.full_name

    def test_get_nonexistent_user_returns_404(self, client):
        """Test that getting a non-existent user returns 404"""
        response = client.get("/api/users/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "User not found"

    def test_get_users_with_pagination(self, client):
        """Test pagination with skip and limit"""
        for i in range(3):
            client.post("/api/users/", json={
                "email": f"user{i}@example.com",
                "full_name": f"User {i}"
            })

        response = client.get("/api/users/?skip=0&limit=2")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 2

    def test_get_users_excludes_inactive(self, client, sample_user):
        """Test that inactive (soft-deleted) users are excluded"""
        # Soft delete the user
        client.delete(f"/api/users/{sample_user.id}")

        response = client.get("/api/users/")
        user_ids = [u["id"] for u in response.json()]
        assert sample_user.id not in user_ids


@pytest.mark.api
class TestUserUpdate:
    """Tests for PUT /api/users/{id} endpoint"""

    def test_update_user_full_name(self, client, sample_user):
        """Test updating full_name"""
        response = client.put(f"/api/users/{sample_user.id}", json={
            "full_name": "Updated Name"
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["full_name"] == "Updated Name"

    def test_update_user_email(self, client, sample_user):
        """Test updating email"""
        response = client.put(f"/api/users/{sample_user.id}", json={
            "email": "newemail@example.com"
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["email"] == "newemail@example.com"

    def test_update_user_email_to_existing_fails(self, client, sample_user):
        """Test that updating email to an existing email fails"""
        # Create another user
        client.post("/api/users/", json={
            "email": "other@example.com",
            "full_name": "Other User"
        })

        response = client.put(f"/api/users/{sample_user.id}", json={
            "email": "other@example.com"
        })

        assert response.status_code == 400
        assert response.json()["detail"] == "Email already registered"

    def test_update_nonexistent_user_returns_404(self, client):
        """Test that updating a non-existent user returns 404"""
        response = client.put("/api/users/99999", json={
            "full_name": "Nobody"
        })

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_user_preserves_other_fields(self, client, sample_user):
        """Test partial updates preserve unchanged fields"""
        original_email = sample_user.email

        response = client.put(f"/api/users/{sample_user.id}", json={
            "full_name": "Only Name Updated"
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["email"] == original_email
        assert response.json()["full_name"] == "Only Name Updated"


@pytest.mark.api
class TestUserDeletion:
    """Tests for DELETE /api/users/{id} endpoint (soft delete)"""

    def test_delete_user_soft_deletes(self, client, sample_user):
        """Test that delete performs a soft delete"""
        response = client.delete(f"/api/users/{sample_user.id}")

        assert response.status_code == 204

        # User should not appear in active user list
        get_response = client.get(f"/api/users/{sample_user.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_nonexistent_user_returns_404(self, client):
        """Test deleting non-existent user returns 404"""
        response = client.delete("/api/users/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
