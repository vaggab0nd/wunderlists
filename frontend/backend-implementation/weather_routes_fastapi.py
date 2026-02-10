"""
FastAPI routes for weather endpoints
Add these routes to your FastAPI application
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict
from datetime import datetime
import uuid
from .weather_service import get_weather_alerts_for_today

router = APIRouter(prefix="/api/weather", tags=["weather"])

# In-memory cache for weather alerts (you can replace this with database storage)
weather_alerts_cache = []


@router.get("/alerts")
async def get_weather_alerts() -> List[Dict]:
    """
    Get all weather alerts for today
    Returns weather information for Dublin and Île de Ré
    """
    try:
        # Fetch fresh weather data
        alerts = await get_weather_alerts_for_today()

        # Add IDs and task_id (you can link these to actual travel day tasks if needed)
        formatted_alerts = []
        for alert in alerts:
            formatted_alert = {
                "id": str(uuid.uuid4()),
                "task_id": "",  # You can link this to an actual task if needed
                "location": alert["location"],
                "date": alert["date"],
                "weather_condition": alert["weather_condition"],
                "temperature": alert["temperature"],
                "alert_type": alert["alert_type"],
                "message": alert["message"],
                "created_at": alert["created_at"]
            }
            formatted_alerts.append(formatted_alert)

        return formatted_alerts

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch weather alerts: {str(e)}")


@router.post("/refresh")
async def refresh_weather_alerts() -> Dict:
    """
    Manually refresh weather data
    This endpoint triggers a fresh fetch from Open-Meteo
    """
    try:
        alerts = await get_weather_alerts_for_today()

        return {
            "success": True,
            "message": f"Successfully refreshed weather data for {len(alerts)} locations",
            "timestamp": datetime.now().isoformat(),
            "locations_updated": [alert["location"] for alert in alerts]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refresh weather alerts: {str(e)}")


# To use these routes, add this to your main FastAPI app:
# from .weather_routes_fastapi import router as weather_router
# app.include_router(weather_router)
