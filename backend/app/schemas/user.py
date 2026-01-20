from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """Base user schema with core fields"""
    email: EmailStr = Field(..., description="User's email address")
    full_name: str = Field(..., min_length=1, max_length=100, description="User's full name")

class UserCreate(UserBase):
    """Schema for creating a new user (simple profile, no auth)"""
    pass

class UserUpdate(BaseModel):
    """Schema for updating a user"""
    email: Optional[EmailStr] = Field(None, description="User's email address")
    full_name: Optional[str] = Field(None, min_length=1, max_length=100, description="User's full name")

class UserResponse(UserBase):
    """Schema for user responses"""
    id: int
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserSummary(BaseModel):
    """Minimal user info for nested responses"""
    id: int
    full_name: str
    email: EmailStr

    class Config:
        from_attributes = True
