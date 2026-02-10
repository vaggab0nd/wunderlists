# Weather Alerts Integration Guide

This directory contains the implementation code for the weather alerts feature using Open-Meteo API.

## Files Included

1. **weather_service.py** - Core weather service that fetches data from Open-Meteo API
2. **weather_routes_fastapi.py** - FastAPI endpoints (use this if you're using FastAPI)
3. **weather_routes_flask.py** - Flask endpoints (use this if you're using Flask)
4. **requirements.txt** - Python dependencies needed

## Features

- Fetches real-time weather for **Dublin, Ireland** and **Île de Ré, France**
- Uses **Open-Meteo** (free, no API key required)
- Returns weather alerts with temperature and conditions
- Distinguishes between "info" and "warning" level alerts
- Supports manual refresh

## Integration Steps

### Step 1: Install Dependencies

Add to your backend's requirements.txt or install directly:

```bash
pip install httpx
```

### Step 2: Copy Files to Your Backend

Copy the following files to your `wunderlists` backend repository:

```
wunderlists/
├── app/
│   ├── weather_service.py          # ← Copy here
│   └── routes/
│       └── weather_routes.py       # ← Copy either fastapi or flask version here
```

### Step 3: Register the Routes

#### For FastAPI:

In your main app file (e.g., `main.py` or `app.py`):

```python
from fastapi import FastAPI
from app.routes.weather_routes_fastapi import router as weather_router

app = FastAPI()

# Register weather routes
app.include_router(weather_router)
```

#### For Flask:

In your main app file (e.g., `app.py`):

```python
from flask import Flask
from app.routes.weather_routes_flask import weather_bp

app = Flask(__name__)

# Register weather blueprint
app.register_blueprint(weather_bp)
```

### Step 4: Test the Endpoints

Start your backend server and test:

```bash
# Get weather alerts
curl http://localhost:8000/api/weather/alerts

# Refresh weather data
curl -X POST http://localhost:8000/api/weather/refresh
```

Expected response from `/api/weather/alerts`:

```json
[
  {
    "id": "uuid-here",
    "task_id": "",
    "location": "Dublin, Ireland",
    "date": "2026-01-20",
    "weather_condition": "Partly cloudy",
    "temperature": 8.5,
    "alert_type": "info",
    "message": "Weather in Dublin, Ireland: Partly cloudy. Temperature: 8.5°C.",
    "created_at": "2026-01-20T14:30:00"
  },
  {
    "id": "uuid-here",
    "task_id": "",
    "location": "Île de Ré, France",
    "date": "2026-01-20",
    "weather_condition": "Clear sky",
    "temperature": 12.3,
    "alert_type": "info",
    "message": "Weather in Île de Ré, France: Clear sky. Temperature: 12.3°C.",
    "created_at": "2026-01-20T14:30:00"
  }
]
```

### Step 5: Deploy to Railway

Once tested locally:

1. Commit and push your changes to the `wunderlists` repository
2. Railway should automatically deploy the new endpoints
3. Your frontend at `https://passionate-perception-production.up.railway.app/api` will now serve the weather data

## Customization

### Change Locations

Edit the `LOCATIONS` dictionary in `weather_service.py`:

```python
LOCATIONS = {
    "Your City": {
        "latitude": 00.0000,
        "longitude": 00.0000,
    },
    "Another City": {
        "latitude": 00.0000,
        "longitude": 00.0000,
    }
}
```

### Link to Travel Day Tasks

Currently, `task_id` is empty. To link weather alerts to specific tasks:

1. Query your tasks database for tasks with `is_travel_day: true`
2. Match the task date to the weather alert date
3. Add the task ID to the alert response

Example modification in `weather_routes_fastapi.py`:

```python
# After getting alerts from get_weather_alerts_for_today()
from .database import get_travel_day_tasks  # Your DB module

travel_tasks = get_travel_day_tasks(date=today)

for alert in formatted_alerts:
    # Find matching task for this date/location
    matching_task = find_matching_task(travel_tasks, alert["date"], alert["location"])
    if matching_task:
        alert["task_id"] = matching_task["id"]
```

## Weather Codes Reference

The service uses WMO Weather interpretation codes from Open-Meteo:

- **0-3**: Clear to cloudy (info)
- **45-48**: Fog (warning)
- **51-67**: Rain (drizzle = info, moderate/heavy = warning)
- **71-77**: Snow (slight = info, moderate/heavy = warning)
- **80-82**: Rain showers (slight = info, moderate/violent = warning)
- **85-86**: Snow showers
- **95-99**: Thunderstorms (all = warning)

## Frontend Integration

The frontend is already configured! The WeatherAlerts component will automatically:

1. Fetch weather data from `/api/weather/alerts` on page load
2. Display alerts with appropriate warning/info styling
3. Allow manual refresh via the refresh button (calls `/api/weather/refresh`)

No frontend changes needed - just deploy the backend endpoints.

## Troubleshooting

### CORS Issues

If you get CORS errors, make sure your backend has CORS enabled:

**FastAPI:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Flask:**
```python
from flask_cors import CORS

CORS(app)
```

### Rate Limiting

Open-Meteo is free for reasonable usage. For production, consider:
- Caching weather data for 15-30 minutes
- Using the `/refresh` endpoint sparingly

### Async in Flask

The Flask version uses a helper function to run async code. For better performance, consider:
- Using Flask with async views (Flask 2.0+)
- Switching to FastAPI for native async support
