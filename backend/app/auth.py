"""
Authentication and Authorization utilities for Wunderlists

This module provides:
- Password hashing and verification
- User context management for Row Level Security
- Authentication middleware
"""
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password for storing."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def set_user_context(db: Session, user_id: int) -> None:
    """
    Set the current user ID in the database session for Row Level Security.

    This function sets a session variable that PostgreSQL RLS policies use
    to filter data. Only data belonging to the current user will be accessible.

    Args:
        db: SQLAlchemy database session
        user_id: ID of the current authenticated user
    """
    try:
        db.execute(text(f"SET LOCAL app.current_user_id = {user_id}"))
        logger.debug(f"User context set for user_id: {user_id}")
    except Exception as e:
        logger.error(f"Failed to set user context: {e}")
        raise


def clear_user_context(db: Session) -> None:
    """
    Clear the current user context from the database session.

    Args:
        db: SQLAlchemy database session
    """
    try:
        db.execute(text("RESET app.current_user_id"))
        logger.debug("User context cleared")
    except Exception as e:
        logger.error(f"Failed to clear user context: {e}")
        raise


def get_current_user_id(db: Session) -> Optional[int]:
    """
    Get the current user ID from the database session.

    Args:
        db: SQLAlchemy database session

    Returns:
        Current user ID or None if not set
    """
    try:
        result = db.execute(text("SELECT current_setting('app.current_user_id', true)"))
        user_id_str = result.scalar()
        return int(user_id_str) if user_id_str else None
    except Exception as e:
        logger.error(f"Failed to get user context: {e}")
        return None
