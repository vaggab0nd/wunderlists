from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta

from backend.app.database import get_db
from backend.app.models.location import Location
from backend.app.models.calendar_event import CalendarEvent
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

@router.get("/alerts/travel")
async def get_travel_weather_alerts(
    days_ahead: int = Query(default=7, ge=1, le=14, description="Number of days to check ahead"),
    db: Session = Depends(get_db)
) -> List[Dict[Any, Any]]:
    """
    Get weather alerts for upcoming calendar events with locations.

    Checks all calendar events in the next N days that have a location,
    fetches weather forecasts for those locations, and returns alerts
    for potentially problematic weather conditions.

    Returns:
        List of alerts with event info and weather conditions
    """
    # Get upcoming events with locations
    now = datetime.now()
    future_date = now + timedelta(days=days_ahead)

    events = db.query(CalendarEvent).filter(
        CalendarEvent.start_time >= now,
        CalendarEvent.start_time <= future_date,
        CalendarEvent.location.isnot(None),
        CalendarEvent.location != ""
    ).order_by(CalendarEvent.start_time).all()

    alerts = []

    for event in events:
        # Parse location (assume format like "City, Country" or just "City")
        location_parts = event.location.split(',')
        city = location_parts[0].strip()
        country = location_parts[1].strip() if len(location_parts) > 1 else None

        # Get weather forecast for event date
        forecast = await weather_service.get_forecast(city, country, days=5)

        if forecast and 'error' not in forecast:
            # Check forecast for the event date
            event_date = event.start_time.date()

            for forecast_item in forecast.get('forecasts', []):
                forecast_date = datetime.fromisoformat(forecast_item['date']).date()

                # If forecast matches event date
                if forecast_date == event_date:
                    description = forecast_item['description'].lower()
                    temp = forecast_item['temperature']

                    # Determine if weather is concerning
                    alert_level = None
                    alert_reason = []

                    # Check for bad weather conditions
                    if any(word in description for word in ['rain', 'shower', 'drizzle']):
                        alert_level = 'warning'
                        alert_reason.append('Rain expected')
                    if any(word in description for word in ['snow', 'sleet', 'ice']):
                        alert_level = 'warning'
                        alert_reason.append('Snow/ice expected')
                    if any(word in description for word in ['storm', 'thunderstorm', 'thunder']):
                        alert_level = 'severe'
                        alert_reason.append('Storms expected')
                    if temp < 0:
                        alert_level = 'warning' if not alert_level else alert_level
                        alert_reason.append(f'Freezing temperatures ({temp}°C)')
                    if temp > 35:
                        alert_level = 'warning' if not alert_level else alert_level
                        alert_reason.append(f'Extreme heat ({temp}°C)')

                    # Only add if there's an alert
                    if alert_level:
                        alerts.append({
                            'event': {
                                'id': event.id,
                                'title': event.title,
                                'start_time': event.start_time.isoformat(),
                                'location': event.location
                            },
                            'alert': {
                                'level': alert_level,
                                'reasons': alert_reason,
                                'temperature': temp,
                                'description': forecast_item['description']
                            }
                        })
                    break

    return alerts
