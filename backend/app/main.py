from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os

from backend.app.database import engine, Base
from backend.app.routes import tasks_router, lists_router, calendar_events_router, locations_router
from backend.app.routes.weather import router as weather_router

# Create database tables
Base.metadata.create_all(bind=engine)

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
    """Health check endpoint"""
    return {"status": "healthy", "service": "wunderlists"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
