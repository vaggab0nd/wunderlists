from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import os
import logging
import time
from sqlalchemy import text
from alembic.config import Config
from alembic import command
import sys
from pathlib import Path

from backend.app.database import engine, Base, SessionLocal
from backend.app.routes import tasks_router, lists_router, calendar_events_router, locations_router
from backend.app.routes.weather import router as weather_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Log environment info for Railway debugging
logger.info(f"Starting Wunderlists application...")
logger.info(f"Environment variables available: DATABASE_URL={bool(os.getenv('DATABASE_URL'))}, "
           f"DATABASE_PRIVATE_URL={bool(os.getenv('DATABASE_PRIVATE_URL'))}, "
           f"PGURL={bool(os.getenv('PGURL'))}")

def run_migrations():
    """Run Alembic migrations on startup"""
    try:
        logger.info("Running database migrations...")

        # Get the alembic.ini path
        alembic_ini = Path(__file__).resolve().parents[3] / "alembic.ini"

        if not alembic_ini.exists():
            logger.warning(f"alembic.ini not found at {alembic_ini}, skipping migrations")
            return False

        # Create Alembic config
        alembic_cfg = Config(str(alembic_ini))

        # Run migrations to latest version
        command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations completed successfully")
        return True

    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        logger.warning("Continuing without migrations - database may be in inconsistent state")
        return False


def init_database_with_retry(max_retries=5, retry_delay=2):
    """Initialize database with retry logic for Railway startup delays"""
    for attempt in range(max_retries):
        try:
            logger.info(f"Database initialization attempt {attempt + 1}/{max_retries}")

            # Test connection first
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            db.close()
            logger.info("Database connection test successful")

            # Run migrations first to ensure schema is up to date
            run_migrations()

            # Create any remaining tables (for new installations)
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully")
            return True

        except Exception as e:
            logger.error(f"Database initialization attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logger.error("All database initialization attempts failed")
                logger.warning("Application will start but database functionality will be limited")
                return False

# Initialize database with retry logic
init_database_with_retry()

app = FastAPI(
    title="Wunderlists - Task Tracking App",
    description="A personal task management and life organization hub",
    version="1.0.0",
    redirect_slashes=False  # Disable automatic trailing slash redirects
)

# CORS middleware configuration for Lovable and other frontends
# Get allowed origins from environment or use permissive defaults
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
if CORS_ORIGINS == "*":
    allowed_origins = ["*"]
else:
    allowed_origins = [origin.strip() for origin in CORS_ORIGINS.split(",")]

# Add common Lovable domains
lovable_origins = [
    "https://lovable.dev",
    "https://*.lovable.dev",
    "https://lovable.app",
    "https://*.lovable.app",
]

# If not using wildcard, add Lovable origins
if "*" not in allowed_origins:
    allowed_origins.extend(lovable_origins)

logger.info(f"CORS configured with origins: {allowed_origins if '*' not in allowed_origins else 'All origins (*)'}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if "*" not in allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log incoming requests for debugging"""
    start_time = time.time()
    origin = request.headers.get("origin", "no-origin")

    logger.info(f"Incoming request: {request.method} {request.url.path} from origin: {origin}")

    try:
        response = await call_next(request)
        duration = time.time() - start_time
        logger.info(f"Request completed: {request.method} {request.url.path} - Status: {response.status_code} - Duration: {duration:.3f}s")
        return response
    except Exception as e:
        logger.error(f"Request failed: {request.method} {request.url.path} - Error: {str(e)}")
        raise

# Exception handlers to ensure CORS headers on errors
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions with CORS headers"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with CORS headers"""
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions with CORS headers"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Log startup information"""
    logger.info("=" * 60)
    logger.info("Wunderlists API Started Successfully")
    logger.info(f"CORS Origins: {allowed_origins if '*' not in allowed_origins else 'All origins (*)'}")
    logger.info(f"Railway Environment: {os.getenv('RAILWAY_ENVIRONMENT', 'local')}")
    logger.info(f"API Docs: http://localhost:8000/docs (or your Railway URL)")
    logger.info("=" * 60)

# Include routers
app.include_router(tasks_router)
app.include_router(lists_router)
app.include_router(calendar_events_router)
app.include_router(locations_router)
app.include_router(weather_router)

# Mount static files
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=os.path.join(frontend_path, "static")), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main dashboard page"""
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
    index_file = os.path.join(frontend_path, "templates", "index.html")

    if os.path.exists(index_file):
        with open(index_file, "r") as f:
            return f.read()
    else:
        return """
        <html>
            <head><title>Wunderlists API</title></head>
            <body>
                <h1>Wunderlists API</h1>
                <p>API is running! Visit <a href="/docs">/docs</a> for API documentation.</p>
            </body>
        </html>
        """

@app.get("/api/ping")
async def ping():
    """Simple ping endpoint to test API connectivity and CORS"""
    return {
        "status": "ok",
        "message": "pong",
        "timestamp": time.time(),
        "service": "wunderlists"
    }

@app.get("/health")
@app.get("/api/health")
async def health_check():
    """Health check endpoint with detailed database diagnostics"""
    health_status = {
        "status": "healthy",
        "service": "wunderlists",
        "version": "1.0.0",
        "timestamp": time.time(),
        "database": {
            "status": "unknown",
            "details": {}
        },
        "environment": {
            "has_database_url": bool(os.getenv("DATABASE_URL")),
            "has_database_private_url": bool(os.getenv("DATABASE_PRIVATE_URL")),
            "has_pgurl": bool(os.getenv("PGURL")),
            "railway_environment": os.getenv("RAILWAY_ENVIRONMENT", "unknown"),
        }
    }

    # Check database connection
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT version()"))
        version = result.fetchone()[0] if result else "unknown"
        db.close()

        health_status["database"]["status"] = "connected"
        health_status["database"]["details"] = {
            "version": version.split()[0:2],  # e.g., ["PostgreSQL", "14.5"]
            "connection_pool": {
                "size": engine.pool.size(),
                "checked_in": engine.pool.checkedin(),
                "checked_out": engine.pool.checkedout(),
                "overflow": engine.pool.overflow()
            }
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["status"] = "degraded"
        health_status["database"]["status"] = "disconnected"
        health_status["database"]["error"] = str(e)
        health_status["database"]["error_type"] = type(e).__name__

    return health_status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
