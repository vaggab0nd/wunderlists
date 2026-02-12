"""
Comprehensive tests for Smart Tasks API endpoints
Tests prioritization logic, urgency scoring, overdue/due-today filtering, and suggestions
"""
import pytest
from datetime import datetime, timedelta
from fastapi import status

from backend.app.models.task import Task, Priority
from backend.app.routes.smart_tasks import calculate_urgency_score


@pytest.mark.api
class TestUrgencyScoreCalculation:
    """Unit tests for the calculate_urgency_score function"""

    def test_base_score_urgent_priority(self):
        """Test base score for urgent priority"""
        task = Task(title="Test", priority=Priority.URGENT)
        score = calculate_urgency_score(task, datetime.now())
        # URGENT=100, no due date=-20 => 80
        assert score == 80

    def test_base_score_high_priority(self):
        """Test base score for high priority"""
        task = Task(title="Test", priority=Priority.HIGH)
        score = calculate_urgency_score(task, datetime.now())
        # HIGH=75, no due date=-20 => 55
        assert score == 55

    def test_base_score_medium_priority(self):
        """Test base score for medium priority"""
        task = Task(title="Test", priority=Priority.MEDIUM)
        score = calculate_urgency_score(task, datetime.now())
        # MEDIUM=50, no due date=-20 => 30
        assert score == 30

    def test_base_score_low_priority(self):
        """Test base score for low priority"""
        task = Task(title="Test", priority=Priority.LOW)
        score = calculate_urgency_score(task, datetime.now())
        # LOW=25, no due date=-20 => 5
        assert score == 5

    def test_overdue_modifier(self):
        """Test overdue task gets +50 modifier"""
        now = datetime.now()
        task = Task(
            title="Test",
            priority=Priority.MEDIUM,
            due_date=now - timedelta(days=2)
        )
        score = calculate_urgency_score(task, now)
        # MEDIUM=50 + overdue=50 => 100
        assert score == 100

    def test_due_today_modifier(self):
        """Test task due today gets +40 modifier"""
        now = datetime.now()
        task = Task(
            title="Test",
            priority=Priority.MEDIUM,
            due_date=now.replace(hour=23, minute=59)
        )
        score = calculate_urgency_score(task, now)
        # MEDIUM=50 + today=40 => 90
        assert score == 90

    def test_due_tomorrow_modifier(self):
        """Test task due tomorrow gets +30 modifier"""
        now = datetime.now()
        task = Task(
            title="Test",
            priority=Priority.MEDIUM,
            due_date=now + timedelta(days=1)
        )
        score = calculate_urgency_score(task, now)
        # MEDIUM=50 + tomorrow=30 => 80
        assert score == 80

    def test_due_this_week_modifier(self):
        """Test task due within a week gets +20 modifier"""
        now = datetime.now()
        task = Task(
            title="Test",
            priority=Priority.MEDIUM,
            due_date=now + timedelta(days=5)
        )
        score = calculate_urgency_score(task, now)
        # MEDIUM=50 + this_week=20 => 70
        assert score == 70

    def test_due_next_week_modifier(self):
        """Test task due within two weeks gets +10 modifier"""
        now = datetime.now()
        task = Task(
            title="Test",
            priority=Priority.MEDIUM,
            due_date=now + timedelta(days=10)
        )
        score = calculate_urgency_score(task, now)
        # MEDIUM=50 + next_week=10 => 60
        assert score == 60

    def test_no_due_date_penalty(self):
        """Test that no due date incurs -20 penalty"""
        task = Task(title="Test", priority=Priority.MEDIUM, due_date=None)
        score = calculate_urgency_score(task, datetime.now())
        # MEDIUM=50 + no_date=-20 => 30
        assert score == 30

    def test_urgent_overdue_highest_score(self):
        """Test that urgent + overdue gives the highest score"""
        now = datetime.now()
        task = Task(
            title="Test",
            priority=Priority.URGENT,
            due_date=now - timedelta(days=1)
        )
        score = calculate_urgency_score(task, now)
        # URGENT=100 + overdue=50 => 150
        assert score == 150


@pytest.mark.api
class TestPrioritizedTasks:
    """Tests for GET /api/tasks/prioritized endpoint"""

    def test_get_prioritized_tasks_empty(self, client):
        """Test getting prioritized tasks when none exist"""
        response = client.get("/api/tasks/prioritized")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_prioritized_tasks_sorted_by_urgency(self, client, multiple_tasks):
        """Test that tasks are sorted by urgency score descending"""
        response = client.get("/api/tasks/prioritized")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # The endpoint only returns incomplete tasks (no is_completed field in response)

        # Verify sorted by urgency_score descending
        scores = [t["urgency_score"] for t in data]
        assert scores == sorted(scores, reverse=True)

    def test_prioritized_tasks_excludes_completed(self, client, sample_completed_task, sample_task):
        """Test that completed tasks are excluded"""
        response = client.get("/api/tasks/prioritized")

        assert response.status_code == status.HTTP_200_OK
        task_ids = [t["id"] for t in response.json()]
        assert sample_completed_task.id not in task_ids

    def test_prioritized_tasks_limit(self, client, multiple_tasks):
        """Test limit parameter"""
        response = client.get("/api/tasks/prioritized?limit=1")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) <= 1

    def test_prioritized_tasks_have_recommendation(self, client, sample_task):
        """Test that each task has a recommendation string"""
        response = client.get("/api/tasks/prioritized")

        assert response.status_code == status.HTTP_200_OK
        for task in response.json():
            assert "recommendation" in task
            assert isinstance(task["recommendation"], str)

    def test_prioritized_tasks_have_urgency_score(self, client, sample_task):
        """Test that each task has an urgency_score"""
        response = client.get("/api/tasks/prioritized")

        assert response.status_code == status.HTTP_200_OK
        for task in response.json():
            assert "urgency_score" in task
            assert isinstance(task["urgency_score"], int)


@pytest.mark.api
class TestOverdueTasks:
    """Tests for GET /api/tasks/overdue endpoint"""

    def test_get_overdue_tasks_empty(self, client):
        """Test when no overdue tasks exist"""
        response = client.get("/api/tasks/overdue")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_get_overdue_tasks(self, client, db_session, sample_user, sample_list):
        """Test getting overdue tasks"""
        # Create an overdue task
        overdue_task = Task(
            title="Overdue Task",
            priority=Priority.HIGH,
            is_completed=False,
            due_date=datetime.now() - timedelta(days=3),
            list_id=sample_list.id,
            user_id=sample_user.id
        )
        db_session.add(overdue_task)
        db_session.commit()

        response = client.get("/api/tasks/overdue")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1
        assert all(t["days_overdue"] > 0 for t in data)

    def test_overdue_tasks_excludes_completed(self, client, db_session, sample_user):
        """Test that completed overdue tasks are excluded"""
        completed_overdue = Task(
            title="Done Overdue",
            priority=Priority.MEDIUM,
            is_completed=True,
            due_date=datetime.now() - timedelta(days=1),
            user_id=sample_user.id
        )
        db_session.add(completed_overdue)
        db_session.commit()

        response = client.get("/api/tasks/overdue")
        titles = [t["title"] for t in response.json()]
        assert "Done Overdue" not in titles

    def test_overdue_tasks_excludes_future_tasks(self, client, db_session, sample_user):
        """Test that future tasks are not included in overdue"""
        future_task = Task(
            title="Future Task",
            priority=Priority.MEDIUM,
            is_completed=False,
            due_date=datetime.now() + timedelta(days=5),
            user_id=sample_user.id
        )
        db_session.add(future_task)
        db_session.commit()

        response = client.get("/api/tasks/overdue")
        titles = [t["title"] for t in response.json()]
        assert "Future Task" not in titles


@pytest.mark.api
class TestDueTodayTasks:
    """Tests for GET /api/tasks/due-today endpoint"""

    def test_get_due_today_empty(self, client):
        """Test when no tasks due today"""
        response = client.get("/api/tasks/due-today")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_get_due_today_tasks(self, client, db_session, sample_user):
        """Test getting tasks due today"""
        now = datetime.now()
        today_task = Task(
            title="Today Task",
            priority=Priority.HIGH,
            is_completed=False,
            due_date=now.replace(hour=14, minute=0, second=0),
            user_id=sample_user.id
        )
        db_session.add(today_task)
        db_session.commit()

        response = client.get("/api/tasks/due-today")

        assert response.status_code == status.HTTP_200_OK
        titles = [t["title"] for t in response.json()]
        assert "Today Task" in titles

    def test_due_today_excludes_completed(self, client, db_session, sample_user):
        """Test that completed tasks due today are excluded"""
        now = datetime.now()
        completed_today = Task(
            title="Done Today",
            priority=Priority.MEDIUM,
            is_completed=True,
            due_date=now.replace(hour=12, minute=0, second=0),
            user_id=sample_user.id
        )
        db_session.add(completed_today)
        db_session.commit()

        response = client.get("/api/tasks/due-today")
        titles = [t["title"] for t in response.json()]
        assert "Done Today" not in titles


@pytest.mark.api
class TestTaskSuggestions:
    """Tests for GET /api/tasks/suggestions endpoint"""

    def test_get_suggestions_returns_disabled(self, client):
        """Test that suggestions endpoint returns disabled status"""
        response = client.get("/api/tasks/suggestions")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["feature_enabled"] is False
        assert data["top_urgent_tasks"] == []
        assert data["suggestions"] == []
        assert data["stats"]["overdue"] == 0
