import httpx
from typing import Optional, Dict, Any
from backend.app.config import get_settings

class WeatherService:
    def __init__(self):
        self.settings = get_settings()
        self.base_url = "https://api.openweathermap.org/data/2.5"

    async def get_current_weather(self, city: str, country: str = None) -> Optional[Dict[Any, Any]]:
        """
        Get current weather for a city

        Args:
            city: City name
            country: Optional country code (ISO 3166)

        Returns:
            Weather data dict or None if error
        """
        if not self.settings.openweather_api_key:
            return {
                "error": "Weather API key not configured",
                "city": city
            }

        query = f"{city},{country}" if country else city

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/weather",
                    params={
                        "q": query,
                        "appid": self.settings.openweather_api_key,
                        "units": "metric"  # Use Celsius
                    },
                    timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()
                    return {
                        "city": data["name"],
                        "country": data["sys"]["country"],
                        "temperature": round(data["main"]["temp"], 1),
                        "feels_like": round(data["main"]["feels_like"], 1),
                        "humidity": data["main"]["humidity"],
                        "description": data["weather"][0]["description"],
                        "icon": data["weather"][0]["icon"],
                        "wind_speed": data["wind"]["speed"]
                    }
                else:
                    return {
                        "error": f"Weather API error: {response.status_code}",
                        "city": city
                    }

        except Exception as e:
            return {
                "error": f"Failed to fetch weather: {str(e)}",
                "city": city
            }

    async def get_forecast(self, city: str, country: str = None, days: int = 5) -> Optional[Dict[Any, Any]]:
        """
        Get weather forecast for a city

        Args:
            city: City name
            country: Optional country code (ISO 3166)
            days: Number of days (1-5)

        Returns:
            Forecast data dict or None if error
        """
        if not self.settings.openweather_api_key:
            return {
                "error": "Weather API key not configured",
                "city": city
            }

        query = f"{city},{country}" if country else city

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/forecast",
                    params={
                        "q": query,
                        "appid": self.settings.openweather_api_key,
                        "units": "metric",
                        "cnt": days * 8  # 8 forecasts per day (3-hour intervals)
                    },
                    timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()
                    forecasts = []

                    for item in data["list"][:days * 8:8]:  # Take one per day
                        forecasts.append({
                            "date": item["dt_txt"],
                            "temperature": round(item["main"]["temp"], 1),
                            "description": item["weather"][0]["description"],
                            "icon": item["weather"][0]["icon"]
                        })

                    return {
                        "city": data["city"]["name"],
                        "country": data["city"]["country"],
                        "forecasts": forecasts
                    }
                else:
                    return {
                        "error": f"Weather API error: {response.status_code}",
                        "city": city
                    }

        except Exception as e:
            return {
                "error": f"Failed to fetch forecast: {str(e)}",
                "city": city
            }
