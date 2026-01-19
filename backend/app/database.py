from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Get DATABASE_URL and handle Railway's postgres:// format
# Railway may provide: DATABASE_URL, DATABASE_PRIVATE_URL, or PGURL
DATABASE_URL = (
    os.getenv("DATABASE_URL") or
    os.getenv("DATABASE_PRIVATE_URL") or
    os.getenv("PGURL") or
    "postgresql://wunderlists_user:password@localhost:5432/wunderlists_db"
)

logger.info(f"Database URL source: {DATABASE_URL.split('@')[0] if '@' in DATABASE_URL else 'default'}")

# Railway uses postgres:// but SQLAlchemy needs postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    logger.info("Converted postgres:// to postgresql:// for SQLAlchemy compatibility")

# Add SSL mode for Railway connections if not already present
if "railway.app" in DATABASE_URL or "railway.internal" in DATABASE_URL:
    if "sslmode" not in DATABASE_URL:
        separator = "&" if "?" in DATABASE_URL else "?"
        DATABASE_URL = f"{DATABASE_URL}{separator}sslmode=require"
        logger.info("Added SSL mode for Railway connection")

# Create engine with connection pooling and error handling
try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using them
        pool_recycle=300,    # Recycle connections after 5 minutes
        pool_size=5,         # Limit connection pool size
        max_overflow=10,     # Max overflow connections
        connect_args={
            "connect_timeout": 10,  # Connection timeout in seconds
        }
    )
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
