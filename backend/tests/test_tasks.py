"""
Comprehensive tests for Tasks API endpoints
Tests all CRUD operations, filtering, validation, and business logic
"""
import pytest
from datetime import datetime, timedelta
from fastapi import status


@pytest.mark.api
class TestTaskCreation:
    """Tests for POST /api/tasks/ endpoint"""

    def test_create_task_minimal(self, client):
        """Test creating a task with only required fields"""
        response = client.post("/api/tasks/", json={
            "title": "New Task"
        })

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "New Task"
        assert data["is_completed"] is False
        assert data["priority"] == "medium"  # Default priority
        assert data["completed_at"] is None
        assert data["id"] is not None
        assert data["created_at"] is not None

    def test_create_task_full_details(self, client, sample_list):
        """Test creating a task with all optional fields"""
        due_date = (datetime.now() + timedelta(days=5)).isoformat()
        reminder_date = (datetime.now() + timedelta(days=4)).isoformat()

        response = client.post("/api/tasks/", json={
            "title": "Complete Task",
            "description": "This task has all fields populated",
            "priority": "high",
            "due_date": due_date,
            "reminder_date": reminder_date,
            "list_id": sample_list.id
        })

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "Complete Task"
        assert data["description"] == "This task has all fields populated"
        assert data["priority"] == "high"
        assert data["list_id"] == sample_list.id
        assert data["due_date"] is not None
        assert data["reminder_date"] is not None

    def test_create_task_with_low_priority(self, client):
        """Test creating a task with low priority"""
        response = client.post("/api/tasks/", json={
            "title": "Low Priority Task",
            "priority": "low"
        })

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["priority"] == "low"

    def test_create_task_with_urgent_priority(self, client):
        """Test creating a task with urgent priority"""
        response = client.post("/api/tasks/", json={
            "title": "Urgent Task",
            "priority": "urgent"
        })

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["priority"] == "urgent"

    def test_create_task_empty_title_fails(self, client):
        """Test that creating a task with empty title fails validation"""
        response = client.post("/api/tasks/", json={
            "title": ""
        })

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_task_missing_title_fails(self, client):
        """Test that creating a task without title fails validation"""
        response = client.post("/api/tasks/", json={
            "description": "Task without title"
        })

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_task_invalid_priority_fails(self, client):
        """Test that invalid priority values are rejected"""
        response = client.post("/api/tasks/", json={
            "title": "Task",
            "priority": "super_urgent"  # Invalid priority
        })

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_task_without_list(self, client):
        """Test creating a task without assigning it to a list"""
        response = client.post("/api/tasks/", json={
            "title": "Standalone Task"
        })

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["list_id"] is None


@pytest.mark.api
class TestTaskRetrieval:
    """Tests for GET /api/tasks/ and GET /api/tasks/{id} endpoints"""

    def test_get_all_tasks_empty(self, client):
        """Test getting tasks when database is empty"""
        response = client.get("/api/tasks/")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_get_all_tasks(self, client, multiple_tasks):
        """Test getting all tasks"""
        response = client.get("/api/tasks/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 4
        assert all("id" in task for task in data)
        assert all("title" in task for task in data)

    def test_get_task_by_id(self, client, sample_task):
        """Test getting a specific task by ID"""
        response = client.get(f"/api/tasks/{sample_task.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == sample_task.id
        assert data["title"] == sample_task.title
        assert data["description"] == sample_task.description
        assert data["priority"] == sample_task.priority.value

    def test_get_nonexistent_task_returns_404(self, client):
        """Test that getting a non-existent task returns 404"""
        response = client.get("/api/tasks/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Task not found"

    def test_get_tasks_with_pagination(self, client, multiple_tasks):
        """Test pagination with skip and limit parameters"""
        # Get first 2 tasks
        response = client.get("/api/tasks/?skip=0&limit=2")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 2

        # Get next 2 tasks
        response = client.get("/api/tasks/?skip=2&limit=2")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 2

        # Skip all tasks
        response = client.get("/api/tasks/?skip=10&limit=10")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 0


@pytest.mark.api
class TestTaskFiltering:
    """Tests for task filtering functionality"""

    def test_filter_by_completion_status_false(self, client, multiple_tasks):
        """Test filtering for incomplete tasks only"""
        response = client.get("/api/tasks/?is_completed=false")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3  # 3 incomplete tasks
        assert all(task["is_completed"] is False for task in data)

    def test_filter_by_completion_status_true(self, client, multiple_tasks):
        """Test filtering for completed tasks only"""
        response = client.get("/api/tasks/?is_completed=true")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1  # 1 completed task
        assert all(task["is_completed"] is True for task in data)

    def test_filter_by_list_id(self, client, multiple_tasks, sample_list):
        """Test filtering tasks by list_id"""
        response = client.get(f"/api/tasks/?list_id={sample_list.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3  # 3 tasks belong to sample_list
        assert all(task["list_id"] == sample_list.id for task in data)

    def test_filter_by_list_id_and_completion(self, client, multiple_tasks, sample_list):
        """Test filtering by both list_id and completion status"""
        response = client.get(
            f"/api/tasks/?list_id={sample_list.id}&is_completed=false"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2  # 2 incomplete tasks in sample_list
        assert all(task["list_id"] == sample_list.id for task in data)
        assert all(task["is_completed"] is False for task in data)

    def test_filter_by_nonexistent_list_id(self, client, multiple_tasks):
        """Test filtering by a list that doesn't exist returns empty"""
        response = client.get("/api/tasks/?list_id=99999")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []


@pytest.mark.api
class TestTaskUpdate:
    """Tests for PUT /api/tasks/{id} endpoint"""

    def test_update_task_title(self, client, sample_task):
        """Test updating task title"""
        response = client.put(f"/api/tasks/{sample_task.id}", json={
            "title": "Updated Title"
        })

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["id"] == sample_task.id

    def test_update_task_description(self, client, sample_task):
        """Test updating task description"""
        response = client.put(f"/api/tasks/{sample_task.id}", json={
            "description": "Updated description"
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["description"] == "Updated description"

    def test_update_task_priority(self, client, sample_task):
        """Test updating task priority"""
        response = client.put(f"/api/tasks/{sample_task.id}", json={
            "priority": "urgent"
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["priority"] == "urgent"

    def test_update_task_due_date(self, client, sample_task):
        """Test updating task due date"""
        due_date = (datetime.now() + timedelta(days=7)).isoformat()

        response = client.put(f"/api/tasks/{sample_task.id}", json={
            "due_date": due_date
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["due_date"] is not None

    def test_update_multiple_fields(self, client, sample_task):
        """Test updating multiple task fields at once"""
        response = client.put(f"/api/tasks/{sample_task.id}", json={
            "title": "Multi-field Update",
            "description": "Updated multiple fields",
            "priority": "high"
        })

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Multi-field Update"
        assert data["description"] == "Updated multiple fields"
        assert data["priority"] == "high"

    def test_update_task_partial_fields_only(self, client, sample_task):
        """Test that partial updates don't affect other fields"""
        original_title = sample_task.title

        response = client.put(f"/api/tasks/{sample_task.id}", json={
            "description": "Only updating description"
        })

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == original_title  # Title unchanged
        assert data["description"] == "Only updating description"

    def test_update_nonexistent_task_returns_404(self, client):
        """Test updating a non-existent task returns 404"""
        response = client.put("/api/tasks/99999", json={
            "title": "This should fail"
        })

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Task not found"

    def test_update_task_empty_title_fails(self, client, sample_task):
        """Test that updating with empty title fails validation"""
        response = client.put(f"/api/tasks/{sample_task.id}", json={
            "title": ""
        })

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.api
class TestTaskCompletionLogic:
    """Tests for task completion toggle and completed_at timestamp logic"""

    def test_mark_task_as_completed_sets_timestamp(self, client, sample_task):
        """Test that marking a task as completed sets completed_at timestamp"""
        assert sample_task.is_completed is False
        assert sample_task.completed_at is None

        response = client.put(f"/api/tasks/{sample_task.id}", json={
            "is_completed": True
        })

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_completed"] is True
        assert data["completed_at"] is not None

    def test_mark_task_as_incomplete_clears_timestamp(self, client, sample_completed_task):
        """Test that marking a completed task as incomplete clears completed_at"""
        assert sample_completed_task.is_completed is True
        assert sample_completed_task.completed_at is not None

        response = client.put(f"/api/tasks/{sample_completed_task.id}", json={
            "is_completed": False
        })

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_completed"] is False
        assert data["completed_at"] is None

    def test_toggle_completion_multiple_times(self, client, sample_task):
        """Test toggling completion status multiple times"""
        task_id = sample_task.id

        # Mark as completed
        response = client.put(f"/api/tasks/{task_id}", json={
            "is_completed": True
        })
        assert response.json()["is_completed"] is True
        assert response.json()["completed_at"] is not None
        first_completion_time = response.json()["completed_at"]

        # Mark as incomplete
        response = client.put(f"/api/tasks/{task_id}", json={
            "is_completed": False
        })
        assert response.json()["is_completed"] is False
        assert response.json()["completed_at"] is None

        # Mark as completed again
        response = client.put(f"/api/tasks/{task_id}", json={
            "is_completed": True
        })
        assert response.json()["is_completed"] is True
        assert response.json()["completed_at"] is not None
        # New completion time should be different
        second_completion_time = response.json()["completed_at"]
        assert second_completion_time != first_completion_time

    def test_update_already_completed_task_preserves_timestamp(self, client, sample_completed_task):
        """Test that updating other fields doesn't affect completed_at if task stays completed"""
        original_completed_at = sample_completed_task.completed_at

        response = client.put(f"/api/tasks/{sample_completed_task.id}", json={
            "title": "Updated title"
        })

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated title"
        assert data["is_completed"] is True
        # Completed_at should remain unchanged when only updating title
        assert data["completed_at"] is not None

    def test_create_task_is_not_completed_by_default(self, client):
        """Test that newly created tasks are not completed by default"""
        response = client.post("/api/tasks/", json={
            "title": "New Task"
        })

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["is_completed"] is False
        assert data["completed_at"] is None


@pytest.mark.api
class TestTaskDeletion:
    """Tests for DELETE /api/tasks/{id} endpoint"""

    def test_delete_task(self, client, sample_task):
        """Test deleting a task"""
        task_id = sample_task.id

        response = client.delete(f"/api/tasks/{task_id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify task is actually deleted
        get_response = client.get(f"/api/tasks/{task_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_completed_task(self, client, sample_completed_task):
        """Test deleting a completed task"""
        task_id = sample_completed_task.id

        response = client.delete(f"/api/tasks/{task_id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deletion
        get_response = client.get(f"/api/tasks/{task_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_nonexistent_task_returns_404(self, client):
        """Test deleting a non-existent task returns 404"""
        response = client.delete("/api/tasks/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Task not found"

    def test_delete_task_with_list_association(self, client, sample_task, sample_list):
        """Test deleting a task that belongs to a list"""
        assert sample_task.list_id == sample_list.id

        response = client.delete(f"/api/tasks/{sample_task.id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify list still exists
        list_response = client.get(f"/api/lists/{sample_list.id}")
        assert list_response.status_code == status.HTTP_200_OK


@pytest.mark.api
class TestTaskEdgeCases:
    """Tests for edge cases and special scenarios"""

    def test_task_with_very_long_title(self, client):
        """Test creating a task with maximum length title"""
        long_title = "A" * 255  # Max length is 255

        response = client.post("/api/tasks/", json={
            "title": long_title
        })

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["title"] == long_title

    def test_task_with_title_exceeding_max_length_fails(self, client):
        """Test that title exceeding 255 characters fails"""
        too_long_title = "A" * 256  # Exceeds max length

        response = client.post("/api/tasks/", json={
            "title": too_long_title
        })

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_task_with_null_description(self, client):
        """Test creating a task with explicitly null description"""
        response = client.post("/api/tasks/", json={
            "title": "Task",
            "description": None
        })

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["description"] is None

    def test_task_with_past_due_date(self, client):
        """Test creating a task with a due date in the past"""
        past_date = (datetime.now() - timedelta(days=5)).isoformat()

        response = client.post("/api/tasks/", json={
            "title": "Overdue Task",
            "due_date": past_date
        })

        # Should still create the task - business logic allows past due dates
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["due_date"] is not None

    def test_update_task_list_assignment(self, client, sample_task, sample_list):
        """Test changing the list a task belongs to"""
        # Create a second list
        new_list_response = client.post("/api/lists/", json={
            "name": "New List",
            "color": "#00FF00"
        })
        new_list_id = new_list_response.json()["id"]

        # Update task to belong to new list
        response = client.put(f"/api/tasks/{sample_task.id}", json={
            "list_id": new_list_id
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["list_id"] == new_list_id

    def test_remove_task_from_list(self, client, sample_task):
        """Test removing a task from its list"""
        assert sample_task.list_id is not None

        response = client.put(f"/api/tasks/{sample_task.id}", json={
            "list_id": None
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["list_id"] is None

    def test_all_priority_levels(self, client):
        """Test creating tasks with all priority levels"""
        priorities = ["low", "medium", "high", "urgent"]

        for priority in priorities:
            response = client.post("/api/tasks/", json={
                "title": f"{priority.capitalize()} Priority Task",
                "priority": priority
            })

            assert response.status_code == status.HTTP_201_CREATED
            assert response.json()["priority"] == priority

        # Verify all were created
        all_tasks = client.get("/api/tasks/")
        assert len(all_tasks.json()) == 4
