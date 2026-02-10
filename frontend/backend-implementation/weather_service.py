"""
Weather Service using Open-Meteo API
Fetches weather data for Dublin, Ireland and Île de Ré, France
"""
import httpx
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Location coordinates
LOCATIONS = {
    "Dublin, Ireland": {
        "latitude": 53.3498,
        "longitude": -6.2603,
    },
    "Île de Ré, France": {
        "latitude": 46.2,
        "longitude": -1.4,
    }
}

# Weather code mapping (WMO Weather interpretation codes)
# https://open-meteo.com/en/docs
WEATHER_CODE_MAP = {
    0: {"condition": "Clear sky", "alert_type": "info"},
    1: {"condition": "Mainly clear", "alert_type": "info"},
    2: {"condition": "Partly cloudy", "alert_type": "info"},
    3: {"condition": "Overcast", "alert_type": "info"},
    45: {"condition": "Fog", "alert_type": "warning"},
    48: {"condition": "Depositing rime fog", "alert_type": "warning"},
    51: {"condition": "Light drizzle", "alert_type": "info"},
    53: {"condition": "Moderate drizzle", "alert_type": "info"},
    55: {"condition": "Dense drizzle", "alert_type": "warning"},
    61: {"condition": "Slight rain", "alert_type": "info"},
    63: {"condition": "Moderate rain", "alert_type": "warning"},
    65: {"condition": "Heavy rain", "alert_type": "warning"},
    71: {"condition": "Slight snow", "alert_type": "info"},
    73: {"condition": "Moderate snow", "alert_type": "warning"},
    75: {"condition": "Heavy snow", "alert_type": "warning"},
    77: {"condition": "Snow grains", "alert_type": "warning"},
    80: {"condition": "Slight rain showers", "alert_type": "info"},
    81: {"condition": "Moderate rain showers", "alert_type": "warning"},
    82: {"condition": "Violent rain showers", "alert_type": "warning"},
    85: {"condition": "Slight snow showers", "alert_type": "info"},
    86: {"condition": "Heavy snow showers", "alert_type": "warning"},
    95: {"condition": "Thunderstorm", "alert_type": "warning"},
    96: {"condition": "Thunderstorm with slight hail", "alert_type": "warning"},
    99: {"condition": "Thunderstorm with heavy hail", "alert_type": "warning"},
}


def get_weather_description(weather_code: int) -> Dict[str, str]:
    """Get weather condition and alert type from weather code"""
    return WEATHER_CODE_MAP.get(
        weather_code,
        {"condition": "Unknown", "alert_type": "info"}
    )


def generate_alert_message(location: str, condition: str, temperature: float, alert_type: str) -> str:
    """Generate a human-readable alert message"""
    if alert_type == "warning":
        return f"⚠️ {condition} expected in {location}. Temperature: {temperature}°C. Consider weather-appropriate preparations."
    else:
        return f"Weather in {location}: {condition}. Temperature: {temperature}°C."


async def fetch_weather_for_location(location_name: str, location_data: Dict) -> Optional[Dict]:
    """Fetch current weather data from Open-Meteo API for a specific location"""
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": location_data["latitude"],
            "longitude": location_data["longitude"],
            "current": "temperature_2m,weather_code",
            "timezone": "auto"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()

            # Extract current weather
            current = data.get("current", {})
            temperature = current.get("temperature_2m")
            weather_code = current.get("weather_code")

            if temperature is None or weather_code is None:
                logger.warning(f"Incomplete weather data for {location_name}")
                return None

            weather_info = get_weather_description(weather_code)

            return {
                "location": location_name,
                "temperature": temperature,
                "weather_condition": weather_info["condition"],
                "alert_type": weather_info["alert_type"],
                "weather_code": weather_code,
                "timestamp": current.get("time", datetime.now().isoformat())
            }

    except httpx.HTTPError as e:
        logger.error(f"HTTP error fetching weather for {location_name}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error fetching weather for {location_name}: {e}")
        return None


async def fetch_all_weather_data() -> List[Dict]:
    """Fetch weather data for all configured locations"""
    weather_data = []

    for location_name, location_coords in LOCATIONS.items():
        weather = await fetch_weather_for_location(location_name, location_coords)
        if weather:
            weather_data.append(weather)

    return weather_data


async def get_weather_alerts_for_today() -> List[Dict]:
    """
    Get weather alerts for today's travel locations
    Returns a list of weather alerts formatted for the frontend
    """
    weather_data = await fetch_all_weather_data()

    alerts = []
    today = datetime.now().date().isoformat()

    for weather in weather_data:
        alert = {
            "location": weather["location"],
            "date": today,
            "weather_condition": weather["weather_condition"],
            "temperature": weather["temperature"],
            "alert_type": weather["alert_type"],
            "message": generate_alert_message(
                weather["location"],
                weather["weather_condition"],
                weather["temperature"],
                weather["alert_type"]
            ),
            "created_at": weather["timestamp"]
        }
        alerts.append(alert)

    return alerts
