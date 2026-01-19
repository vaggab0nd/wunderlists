from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
import logging
import time
from sqlalchemy import text

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

            # Create tables
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
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/health")
async def health_check():
    """Health check endpoint with detailed database diagnostics"""
    health_status = {
        "status": "healthy",
        "service": "wunderlists",
        "database": {
            "status": "unknown",
            "details": {}
        },
        "environment": {
            "has_database_url": bool(os.getenv("DATABASE_URL")),
            "has_database_private_url": bool(os.getenv("DATABASE_PRIVATE_URL")),
            "has_pgurl": bool(os.getenv("PGURL")),
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
