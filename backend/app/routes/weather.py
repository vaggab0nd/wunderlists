from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from backend.app.database import get_db
from backend.app.models.location import Location
from backend.app.services.weather import WeatherService

router = APIRouter(prefix="/api/weather", tags=["weather"])
weather_service = WeatherService()

@router.get("/current/{location_id}")
async def get_weather_for_location(location_id: int, db: Session = Depends(get_db)) -> Dict[Any, Any]:
    """Get current weather for a saved location"""
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    weather = await weather_service.get_current_weather(location.city, location.country)
    return {
        "location": {
            "id": location.id,
            "name": location.name,
            "city": location.city,
            "country": location.country
        },
        "weather": weather
    }

@router.get("/dashboard")
async def get_dashboard_weather(db: Session = Depends(get_db)) -> List[Dict[Any, Any]]:
    """Get current weather for all dashboard locations"""
    locations = db.query(Location).filter(Location.show_in_dashboard == True).all()

    weather_data = []
    for location in locations:
        weather = await weather_service.get_current_weather(location.city, location.country)
        weather_data.append({
            "location": {
                "id": location.id,
                "name": location.name,
                "city": location.city,
                "country": location.country
            },
            "weather": weather
        })

    return weather_data

@router.get("/forecast/{location_id}")
async def get_forecast_for_location(
    location_id: int,
    days: int = Query(default=5, ge=1, le=5),
    db: Session = Depends(get_db)
) -> Dict[Any, Any]:
    """Get weather forecast for a saved location"""
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    forecast = await weather_service.get_forecast(location.city, location.country, days)
    return {
        "location": {
            "id": location.id,
            "name": location.name,
            "city": location.city,
            "country": location.country
        },
        "forecast": forecast
    }
