#!/usr/bin/env python3
"""
Railway Database Diagnostics Script
Run this to diagnose database connection issues on Railway
"""
import os
import sys
from sqlalchemy import create_engine, text

def check_environment():
    """Check for Railway environment variables"""
    print("=" * 60)
    print("RAILWAY ENVIRONMENT CHECK")
    print("=" * 60)

    env_vars = [
        "DATABASE_URL",
        "DATABASE_PRIVATE_URL",
        "PGURL",
        "PORT",
        "RAILWAY_ENVIRONMENT",
        "RAILWAY_PROJECT_ID"
    ]

    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive data
            if "DATABASE" in var or "PGURL" in var:
                if "@" in value:
                    parts = value.split("@")
                    masked = f"{parts[0].split('//')[0]}//***:***@{parts[1]}"
                    print(f"✓ {var}: {masked}")
                else:
                    print(f"✓ {var}: ***")
            else:
                print(f"✓ {var}: {value}")
        else:
            print(f"✗ {var}: NOT SET")

    print()

def test_database_connection():
    """Test database connection"""
    print("=" * 60)
    print("DATABASE CONNECTION TEST")
    print("=" * 60)

    # Try different environment variable names
    DATABASE_URL = (
        os.getenv("DATABASE_URL") or
        os.getenv("DATABASE_PRIVATE_URL") or
        os.getenv("PGURL")
    )

    if not DATABASE_URL:
        print("✗ No database URL found in environment variables!")
        print("\nTroubleshooting steps:")
        print("1. Go to your Railway project dashboard")
        print("2. Click on your database service")
        print("3. Go to 'Variables' tab")
        print("4. Ensure DATABASE_URL is set")
        print("5. In your app service, add the database as a reference")
        return False

    print(f"Database URL found: {DATABASE_URL.split('@')[0] if '@' in DATABASE_URL else 'invalid format'}...")

    # Convert postgres:// to postgresql://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        print("✓ Converted postgres:// to postgresql://")

    # Test connection
    try:
        print("\nAttempting to connect...")
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 10}
        )

        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✓ Connection successful!")
            print(f"✓ PostgreSQL version: {version}")

            # Check if tables exist
            result = conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
            """))
            tables = [row[0] for row in result]
            if tables:
                print(f"✓ Found {len(tables)} tables: {', '.join(tables)}")
            else:
                print("⚠ No tables found - database might need initialization")

        return True

    except Exception as e:
        print(f"✗ Connection failed: {e}")
        print(f"\nError type: {type(e).__name__}")
        print("\nCommon issues:")
        print("1. Database service not started on Railway")
        print("2. Wrong DATABASE_URL format")
        print("3. Network/firewall issues")
        print("4. Database credentials changed")
        return False

def main():
    print("\n" + "=" * 60)
    print("RAILWAY DATABASE DIAGNOSTICS")
    print("=" * 60 + "\n")

    check_environment()
    success = test_database_connection()

    print("\n" + "=" * 60)
    if success:
        print("✓ DIAGNOSTICS PASSED - Database connection working!")
    else:
        print("✗ DIAGNOSTICS FAILED - See errors above")
    print("=" * 60 + "\n")

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
