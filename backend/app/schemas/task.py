from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    is_travel_day: bool = False
    priority: Priority = Priority.MEDIUM
    due_date: Optional[datetime] = None
    reminder_date: Optional[datetime] = None
    list_id: Optional[int] = None
    user_id: Optional[int] = Field(None, description="User assigned to this task")

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    is_travel_day: Optional[bool] = None
    priority: Optional[Priority] = None
    due_date: Optional[datetime] = None
    reminder_date: Optional[datetime] = None
    list_id: Optional[int] = None
    user_id: Optional[int] = Field(None, description="User assigned to this task")

class TaskResponse(TaskBase):
    id: int
    is_completed: bool
    is_travel_day: bool
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
