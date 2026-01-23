"""
Weather Alerts Routes - Open-Meteo Integration

Provides weather alerts for tasks marked as travel days.
Monitors weather for Dublin and Île de Ré.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging

from backend.app.database import get_db
from backend.app.models.task import Task
from backend.app.services.open_meteo_weather import OpenMeteoWeatherService

router = APIRouter(prefix="/api/weather", tags=["weather-alerts"])
weather_service = OpenMeteoWeatherService()
logger = logging.getLogger(__name__)


@router.get("/alerts")
async def get_weather_alerts(
    days_ahead: int = Query(default=7, ge=1, le=14, description="Number of days to check ahead"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get weather alerts for tasks marked as travel days.

    Checks all tasks with is_travel_day=true in the next N days,
    fetches weather forecasts for Dublin and Île de Ré,
    and returns alerts for potentially problematic weather conditions.

    Returns:
        {
            "alerts": [
                {
                    "task": {...},
                    "weather": {
                        "Dublin": {...},
                        "Île de Ré": {...}
                    }
                }
            ],
            "summary": {
                "total_alerts": 5,
                "warning_count": 2,
                "info_count": 3,
                "travel_days_checked": 3
            }
        }
    """
    logger.info(f"Fetching weather alerts for next {days_ahead} days")

    # Get upcoming travel day tasks
    now = datetime.now()
    future_date = now + timedelta(days=days_ahead)

    travel_tasks = db.query(Task).filter(
        Task.is_travel_day == True,
        Task.is_completed == False,
        Task.due_date >= now,
        Task.due_date <= future_date
    ).order_by(Task.due_date).all()

    logger.info(f"Found {len(travel_tasks)} travel day tasks")

    alerts = []
    warning_count = 0
    info_count = 0

    for task in travel_tasks:
        if not task.due_date:
            continue

        task_date = task.due_date.date()
        task_datetime = datetime.combine(task_date, datetime.min.time())

        # Get weather alerts for both locations
        weather_data = await weather_service.get_alerts_for_all_locations(task_datetime)

        # Only include if there are alerts
        if weather_data:
            task_alert = {
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "due_date": task.due_date.isoformat(),
                    "priority": task.priority.value if task.priority else "medium"
                },
                "weather": {}
            }

            # Organize weather by location
            for location_weather in weather_data:
                location_name = location_weather["location"]
                task_alert["weather"][location_name] = location_weather

                # Count alert types
                if location_weather["alert"]:
                    if location_weather["alert"]["type"] == "warning":
                        warning_count += 1
                    elif location_weather["alert"]["type"] == "info":
                        info_count += 1

            alerts.append(task_alert)

    summary = {
        "total_alerts": warning_count + info_count,
        "warning_count": warning_count,
        "info_count": info_count,
        "travel_days_checked": len(travel_tasks),
        "date_range": {
            "from": now.date().isoformat(),
            "to": future_date.date().isoformat()
        }
    }

    logger.info(f"Generated {len(alerts)} task alerts with {summary['total_alerts']} weather alerts")

    return {
        "alerts": alerts,
        "summary": summary
    }


@router.get("/refresh")
async def refresh_weather_alerts(
    days_ahead: int = Query(default=7, ge=1, le=14, description="Number of days to check ahead"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Manually trigger a refresh of weather alert data.

    This is essentially the same as /alerts but with explicit refresh semantics.
    Useful for frontend "Refresh" buttons or scheduled jobs.

    Returns:
        Same format as /alerts endpoint with additional refresh metadata
    """
    logger.info(f"Manual weather refresh requested for next {days_ahead} days")

    # Get the alert data
    alert_data = await get_weather_alerts(days_ahead=days_ahead, db=db)

    # Add refresh metadata
    return {
        **alert_data,
        "refresh_metadata": {
            "refreshed_at": datetime.now().isoformat(),
            "requested_days": days_ahead,
            "data_source": "Open-Meteo API (free)",
            "locations": ["Dublin, Ireland", "Île de Ré, France"]
        }
    }


@router.get("/test")
async def test_weather_service() -> Dict[str, Any]:
    """
    Test endpoint to verify Open-Meteo API is working.

    Returns weather for both locations for tomorrow.
    """
    logger.info("Testing Open-Meteo weather service")

    tomorrow = datetime.now() + timedelta(days=1)

    dublin_weather = await weather_service.get_weather_for_date("Dublin", tomorrow)
    ile_de_re_weather = await weather_service.get_weather_for_date("Île de Ré", tomorrow)

    return {
        "status": "ok",
        "test_date": tomorrow.date().isoformat(),
        "locations": {
            "Dublin": dublin_weather,
            "Île de Ré": ile_de_re_weather
        },
        "message": "Open-Meteo API is working correctly" if (dublin_weather and ile_de_re_weather) else "Failed to fetch weather data"
    }


@router.get("/current")
async def get_current_weather() -> Dict[str, Any]:
    """
    Get current weather for both Dublin and Île de Ré.

    This endpoint provides real-time weather data for the dashboard weather panel.
    Unlike /alerts, this always returns weather data regardless of travel tasks.

    Returns:
        {
            "locations": [
                {
                    "location": "Dublin, Ireland",
                    "location_key": "Dublin",
                    "temperature": 12.5,
                    "temperature_max": 15.0,
                    "temperature_min": 10.0,
                    "weather_description": "Partly cloudy",
                    "weathercode": 2,
                    "windspeed_kmh": 15.0,
                    "humidity": 75
                },
                ...
            ],
            "updated_at": "2024-01-18T10:00:00Z"
        }
    """
    logger.info("Fetching current weather for dashboard locations")

    locations_weather = []

    # Fetch weather for both locations
    for location_key in ["Dublin", "Île de Ré"]:
        weather = await weather_service.get_current_weather(location_key)

        if weather:
            locations_weather.append(weather)
        else:
            logger.warning(f"Failed to fetch weather for {location_key}")
            # Return error info so frontend can show something
            locations_weather.append({
                "location": f"{location_key}, Ireland" if location_key == "Dublin" else f"{location_key}, France",
                "location_key": location_key,
                "error": "Failed to fetch weather data",
                "temperature": None,
                "weather_description": "Unavailable"
            })

    return {
        "locations": locations_weather,
        "updated_at": datetime.now().isoformat(),
        "data_source": "Open-Meteo"
    }


@router.get("/locations")
async def get_monitored_locations() -> Dict[str, Any]:
    """
    Get information about the hardcoded locations being monitored.
    """
    return {
        "locations": [
            {
                "key": "Dublin",
                "name": "Dublin, Ireland",
                "coordinates": {
                    "latitude": 53.3498,
                    "longitude": -6.2603
                },
                "timezone": "Europe/Dublin"
            },
            {
                "key": "Île de Ré",
                "name": "Île de Ré, France",
                "coordinates": {
                    "latitude": 46.2,
                    "longitude": -1.4
                },
                "timezone": "Europe/Paris"
            }
        ],
        "data_source": {
            "name": "Open-Meteo",
            "url": "https://open-meteo.com/",
            "api_key_required": False,
            "features": [
                "7-day forecast",
                "Temperature (min/max)",
                "Precipitation probability",
                "Wind speed",
                "Weather codes (30+ conditions)"
            ]
        }
    }
