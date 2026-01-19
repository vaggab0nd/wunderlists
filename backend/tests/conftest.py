"""
Pytest configuration and fixtures for Wunderlists tests
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime, timedelta

from backend.app.database import Base, get_db
from backend.app.main import app
from backend.app.models.task import Task, Priority
from backend.app.models.list import List
from backend.app.models.user import User
from backend.app.models.calendar_event import CalendarEvent
from backend.app.models.location import Location


# Use in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def db_engine():
    """Create a fresh database engine for each test"""
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create a new database session for each test"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with overridden database dependency"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# Sample data fixtures

@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing"""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashedpassword123",
        full_name="Test User",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_list(db_session, sample_user):
    """Create a sample list for testing"""
    list_obj = List(
        name="Test List",
        description="A test list",
        color="#FF5733",
        icon="📝",
        user_id=sample_user.id
    )
    db_session.add(list_obj)
    db_session.commit()
    db_session.refresh(list_obj)
    return list_obj


@pytest.fixture
def sample_task(db_session, sample_list, sample_user):
    """Create a sample task for testing"""
    task = Task(
        title="Test Task",
        description="This is a test task",
        priority=Priority.MEDIUM,
        is_completed=False,
        list_id=sample_list.id,
        user_id=sample_user.id
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    return task


@pytest.fixture
def sample_completed_task(db_session, sample_list, sample_user):
    """Create a sample completed task for testing"""
    task = Task(
        title="Completed Task",
        description="This task is completed",
        priority=Priority.HIGH,
        is_completed=True,
        completed_at=datetime.now(),
        list_id=sample_list.id,
        user_id=sample_user.id
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    return task


@pytest.fixture
def multiple_tasks(db_session, sample_list, sample_user):
    """Create multiple tasks with different properties"""
    tasks = []

    # Low priority, not completed
    task1 = Task(
        title="Low Priority Task",
        priority=Priority.LOW,
        is_completed=False,
        list_id=sample_list.id,
        user_id=sample_user.id
    )
    tasks.append(task1)

    # Medium priority, completed
    task2 = Task(
        title="Medium Priority Task",
        priority=Priority.MEDIUM,
        is_completed=True,
        completed_at=datetime.now(),
        list_id=sample_list.id,
        user_id=sample_user.id
    )
    tasks.append(task2)

    # High priority, not completed, with due date
    task3 = Task(
        title="High Priority Task",
        priority=Priority.HIGH,
        is_completed=False,
        due_date=datetime.now() + timedelta(days=3),
        list_id=sample_list.id,
        user_id=sample_user.id
    )
    tasks.append(task3)

    # Urgent priority, not completed
    task4 = Task(
        title="Urgent Task",
        priority=Priority.URGENT,
        is_completed=False,
        user_id=sample_user.id
        # No list_id - task without a list
    )
    tasks.append(task4)

    for task in tasks:
        db_session.add(task)

    db_session.commit()

    for task in tasks:
        db_session.refresh(task)

    return tasks


@pytest.fixture
def sample_calendar_event(db_session, sample_user):
    """Create a sample calendar event for testing"""
    event = CalendarEvent(
        title="Test Event",
        description="A test event",
        start_time=datetime.now() + timedelta(hours=2),
        end_time=datetime.now() + timedelta(hours=3),
        location="Test Location",
        user_id=sample_user.id
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    return event


@pytest.fixture
def sample_location(db_session, sample_user):
    """Create a sample location for testing"""
    location = Location(
        name="Test City",
        city="TestCity",
        country="TestCountry",
        latitude=40.7128,
        longitude=-74.0060,
        show_in_dashboard=True,
        user_id=sample_user.id
    )
    db_session.add(location)
    db_session.commit()
    db_session.refresh(location)
    return location
