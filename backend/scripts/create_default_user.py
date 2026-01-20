#!/usr/bin/env python3
"""
Script to create a default user in the database.
This ensures there's always at least one user for the application.
"""

import sys
from pathlib import Path

# Add parent directory to path to import backend modules
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.app.database import SessionLocal
from backend.app.models.user import User
import hashlib

def generate_dummy_password(email: str) -> str:
    """Generate a dummy hashed password for simple user profiles (no real auth)"""
    return hashlib.sha256(f"dummy_{email}".encode()).hexdigest()

def create_default_user():
    """Create the default user Joe O'Reilly if it doesn't exist"""
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == "joeoreilly@gmail.com").first()

        if existing_user:
            print(f"✓ Default user already exists: {existing_user.full_name} ({existing_user.email})")
            print(f"  User ID: {existing_user.id}")
            print(f"  Active: {existing_user.is_active}")
            return existing_user

        # Create the default user
        default_user = User(
            email="joeoreilly@gmail.com",
            username="joeoreilly",
            full_name="Joe O'Reilly",
            hashed_password=generate_dummy_password("joeoreilly@gmail.com"),
            is_active=True,
            is_superuser=False
        )

        db.add(default_user)
        db.commit()
        db.refresh(default_user)

        print(f"✓ Created default user: {default_user.full_name} ({default_user.email})")
        print(f"  User ID: {default_user.id}")
        print(f"  Username: {default_user.username}")

        return default_user

    except Exception as e:
        print(f"✗ Error creating default user: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating default user...")
    create_default_user()
    print("Done!")
