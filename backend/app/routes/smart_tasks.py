"""
Smart task prioritization and suggestions.

Provides intelligent task recommendations based on:
- Due dates (urgency)
- Priority levels
- Completion status
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta

from backend.app.database import get_db
from backend.app.models.task import Task, Priority

router = APIRouter(tags=["smart-tasks"])

def calculate_urgency_score(task: Task, now: datetime) -> int:
    """
    Calculate an urgency score for a task based on priority and due date.

    Score breakdown:
    - Base priority: URGENT=100, HIGH=75, MEDIUM=50, LOW=25
    - Due date modifier: Overdue=+50, Today=+40, Tomorrow=+30, This week=+20, Next week=+10
    - No due date: -20

    Returns:
        int: Urgency score (higher = more urgent)
    """
    # Base score from priority
    priority_scores = {
        Priority.URGENT: 100,
        Priority.HIGH: 75,
        Priority.MEDIUM: 50,
        Priority.LOW: 25
    }

    score = priority_scores.get(task.priority, 50)

    # Add due date modifier
    if task.due_date:
        due_date = task.due_date.date() if hasattr(task.due_date, 'date') else task.due_date
        today = now.date()

        days_until_due = (due_date - today).days

        if days_until_due < 0:
            # Overdue
            score += 50
        elif days_until_due == 0:
            # Due today
            score += 40
        elif days_until_due == 1:
            # Due tomorrow
            score += 30
        elif days_until_due <= 7:
            # Due this week
            score += 20
        elif days_until_due <= 14:
            # Due next week
            score += 10
    else:
        # No due date - lower priority
        score -= 20

    return score

@router.get("/prioritized")
def get_prioritized_tasks(
    limit: int = Query(default=10, ge=1, le=50, description="Number of tasks to return"),
    user_id: int = Query(default=None, description="Filter by user ID"),
    db: Session = Depends(get_db)
) -> List[Dict[Any, Any]]:
    """
    Get tasks ordered by smart priority.

    Returns incomplete tasks sorted by urgency score (combination of priority and due date).
    Most urgent tasks appear first.

    Args:
        limit: Maximum number of tasks to return
        user_id: Optional user filter

    Returns:
        List of tasks with urgency scores and recommendations
    """
    # Get incomplete tasks
    query = db.query(Task).filter(Task.is_completed == False)

    if user_id:
        query = query.filter(Task.user_id == user_id)

    tasks = query.all()

    now = datetime.now()

    # Calculate urgency scores
    task_scores = []
    for task in tasks:
        score = calculate_urgency_score(task, now)
        task_scores.append({
            'task': task,
            'urgency_score': score
        })

    # Sort by urgency score (descending)
    task_scores.sort(key=lambda x: x['urgency_score'], reverse=True)

    # Format results
    results = []
    for item in task_scores[:limit]:
        task = item['task']
        score = item['urgency_score']

        # Determine recommendation
        recommendation = None
        if score >= 120:
            recommendation = "Critical - Handle immediately!"
        elif score >= 100:
            recommendation = "Urgent - Do this today"
        elif score >= 80:
            recommendation = "High priority - Schedule soon"
        elif score >= 60:
            recommendation = "Medium priority - This week"
        else:
            recommendation = "Low priority - When you have time"

        # Calculate days until due
        days_until_due = None
        if task.due_date:
            due_date = task.due_date.date() if hasattr(task.due_date, 'date') else task.due_date
            days_until_due = (due_date - now.date()).days

        results.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'priority': task.priority.value,
            'due_date': task.due_date.isoformat() if task.due_date else None,
            'days_until_due': days_until_due,
            'urgency_score': score,
            'recommendation': recommendation,
            'list_id': task.list_id,
            'user_id': task.user_id,
            'created_at': task.created_at.isoformat()
        })

    return results

@router.get("/overdue")
def get_overdue_tasks(
    user_id: int = Query(default=None, description="Filter by user ID"),
    db: Session = Depends(get_db)
) -> List[Dict[Any, Any]]:
    """
    Get all overdue tasks.

    Returns incomplete tasks that are past their due date.

    Args:
        user_id: Optional user filter

    Returns:
        List of overdue tasks
    """
    now = datetime.now()

    query = db.query(Task).filter(
        Task.is_completed == False,
        Task.due_date < now
    )

    if user_id:
        query = query.filter(Task.user_id == user_id)

    tasks = query.order_by(Task.due_date.asc()).all()

    results = []
    for task in tasks:
        days_overdue = (now.date() - task.due_date.date()).days

        results.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'priority': task.priority.value,
            'due_date': task.due_date.isoformat(),
            'days_overdue': days_overdue,
            'list_id': task.list_id,
            'user_id': task.user_id,
            'created_at': task.created_at.isoformat()
        })

    return results

@router.get("/due-today")
def get_due_today_tasks(
    user_id: int = Query(default=None, description="Filter by user ID"),
    db: Session = Depends(get_db)
) -> List[Dict[Any, Any]]:
    """
    Get tasks due today.

    Returns incomplete tasks with a due date of today.

    Args:
        user_id: Optional user filter

    Returns:
        List of tasks due today
    """
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    query = db.query(Task).filter(
        Task.is_completed == False,
        Task.due_date >= today_start,
        Task.due_date <= today_end
    )

    if user_id:
        query = query.filter(Task.user_id == user_id)

    tasks = query.order_by(Task.priority.desc()).all()

    results = []
    for task in tasks:
        results.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'priority': task.priority.value,
            'due_date': task.due_date.isoformat(),
            'list_id': task.list_id,
            'user_id': task.user_id,
            'created_at': task.created_at.isoformat()
        })

    return results

@router.get("/suggestions")
def get_task_suggestions(
    user_id: int = Query(default=None, description="Filter by user ID"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get comprehensive task suggestions and statistics.

    CURRENTLY DISABLED - Returns empty data to hide the suggestions box.

    Args:
        user_id: Optional user filter

    Returns:
        Dict with empty task statistics (feature disabled)
    """
    # Feature temporarily disabled - return empty data
    # Frontend will hide the suggestions box when there are no suggestions
    return {
        'stats': {
            'overdue': 0,
            'due_today': 0,
            'due_this_week': 0,
            'total_incomplete': 0,
            'total_completed': 0
        },
        'top_urgent_tasks': [],
        'suggestions': [],
        'feature_enabled': False  # Signal to frontend that this feature is disabled
    }
