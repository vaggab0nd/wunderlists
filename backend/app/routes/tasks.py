from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from backend.app.database import get_db
from backend.app.models.task import Task
from backend.app.schemas.task import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

def _get_tasks_impl(
    skip: int = 0,
    limit: int = 100,
    list_id: int = None,
    is_completed: bool = None,
    db: Session = Depends(get_db)
):
    """Implementation for getting all tasks with optional filtering"""
    query = db.query(Task)

    if list_id is not None:
        query = query.filter(Task.list_id == list_id)
    if is_completed is not None:
        query = query.filter(Task.is_completed == is_completed)

    tasks = query.offset(skip).limit(limit).all()
    return tasks

@router.get("/", response_model=List[TaskResponse])
@router.get("", response_model=List[TaskResponse])
def get_tasks(
    skip: int = 0,
    limit: int = 100,
    list_id: int = None,
    is_completed: bool = None,
    db: Session = Depends(get_db)
):
    """Get all tasks with optional filtering"""
    return _get_tasks_impl(skip, limit, list_id, is_completed, db)

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get a specific task by ID"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Create a new task"""
    db_task = Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    """Update a task"""
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_update.model_dump(exclude_unset=True)

    # Handle completion status
    if "is_completed" in update_data:
        if update_data["is_completed"] and not db_task.is_completed:
            update_data["completed_at"] = datetime.now()
        elif not update_data["is_completed"]:
            update_data["completed_at"] = None

    for field, value in update_data.items():
        setattr(db_task, field, value)

    db.commit()
    db.refresh(db_task)
    return db_task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a task"""
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(db_task)
    db.commit()
    return None
