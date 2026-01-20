from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.schemas.user import UserCreate, UserUpdate, UserResponse
import hashlib

router = APIRouter(prefix="/api/users", tags=["users"])

def generate_dummy_password(email: str) -> str:
    """Generate a dummy hashed password for simple user profiles (no real auth)"""
    # This is just a placeholder since the User model requires hashed_password
    # In a real auth system, this would be properly hashed with bcrypt
    return hashlib.sha256(f"dummy_{email}".encode()).hexdigest()

@router.post("/", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user profile.

    This is a simple user management system without authentication.
    Users are created with just a name and email.
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Generate username from email (before @ symbol)
    username = user.email.split('@')[0]

    # Check if username exists, if so append number
    base_username = username
    counter = 1
    while db.query(User).filter(User.username == username).first():
        username = f"{base_username}{counter}"
        counter += 1

    # Create user with dummy password (not used for auth)
    db_user = User(
        email=user.email,
        username=username,
        full_name=user.full_name,
        hashed_password=generate_dummy_password(user.email),
        is_active=True,
        is_superuser=False
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/", response_model=List[UserResponse])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all users.

    Supports pagination with skip and limit parameters.
    """
    users = db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user by ID."""
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """
    Update a user's profile.

    Only email and full_name can be updated.
    """
    db_user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if new email is already taken by another user
    if user_update.email and user_update.email != db_user.email:
        existing = db.query(User).filter(User.email == user_update.email, User.id != user_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

    # Update fields
    if user_update.email is not None:
        db_user.email = user_update.email
    if user_update.full_name is not None:
        db_user.full_name = user_update.full_name

    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete a user (soft delete by setting is_active to False).

    Note: This does NOT cascade delete tasks, lists, etc.
    Those will remain but will have user_id set to NULL.
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Soft delete
    db_user.is_active = False
    db.commit()
    return None
