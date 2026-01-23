"""
Open-Meteo Weather Service for Dublin and Île de Ré

Free weather API (no key needed) providing forecasts for two hardcoded locations.
Generates user-friendly alerts for weather conditions that may affect travel.
"""
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class OpenMeteoWeatherService:
    """
    Weather service using Open-Meteo API (https://open-meteo.com/)

    Hardcoded locations:
    - Dublin, Ireland: 53.3498°N, 6.2603°W
    - Île de Ré, France: 46.2°N, 1.4°W
    """

    # Hardcoded location coordinates
    LOCATIONS = {
        "Dublin": {
            "name": "Dublin, Ireland",
            "latitude": 53.3498,
            "longitude": -6.2603,
            "timezone": "Europe/Dublin"
        },
        "Île de Ré": {
            "name": "Île de Ré, France",
            "latitude": 46.2,
            "longitude": -1.4,
            "timezone": "Europe/Paris"
        }
    }

    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1/forecast"

    async def get_current_weather(
        self,
        location_key: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get current weather for a location (today's forecast).

        Args:
            location_key: "Dublin" or "Île de Ré"

        Returns:
            Weather data dict with temperature, conditions, and basic info
        """
        if location_key not in self.LOCATIONS:
            logger.error(f"Unknown location: {location_key}")
            return None

        location = self.LOCATIONS[location_key]

        try:
            # Open-Meteo free API parameters for current weather
            params = {
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "timezone": location["timezone"],
                "current": [
                    "temperature_2m",
                    "weathercode",
                    "windspeed_10m",
                    "relative_humidity_2m"
                ],
                "daily": [
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "weathercode"
                ],
                "forecast_days": 1
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    params=params,
                    timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()

                    # Extract current weather
                    current = data.get("current", {})
                    daily = data.get("daily", {})

                    temp_current = current.get("temperature_2m", 0)
                    weathercode = current.get("weathercode", 0)
                    windspeed = current.get("windspeed_10m", 0)
                    humidity = current.get("relative_humidity_2m", 0)

                    # Get today's min/max from daily forecast
                    temp_max = daily.get("temperature_2m_max", [temp_current])[0]
                    temp_min = daily.get("temperature_2m_min", [temp_current])[0]

                    # Interpret weather code
                    weather_description = self._interpret_weather_code(weathercode)

                    return {
                        "location": location["name"],
                        "location_key": location_key,
                        "temperature": round(temp_current, 1),
                        "temperature_max": round(temp_max, 1),
                        "temperature_min": round(temp_min, 1),
                        "weather_description": weather_description,
                        "weathercode": weathercode,
                        "windspeed_kmh": round(windspeed, 1),
                        "humidity": humidity
                    }
                else:
                    logger.error(f"Open-Meteo API error: {response.status_code}")
                    return None

        except Exception as e:
            logger.error(f"Failed to fetch current weather from Open-Meteo: {str(e)}", exc_info=True)
            return None

    async def get_weather_for_date(
        self,
        location_key: str,
        target_date: datetime
    ) -> Optional[Dict[str, Any]]:
        """
        Get weather forecast for a specific date at a location.

        Args:
            location_key: "Dublin" or "Île de Ré"
            target_date: The date to get weather for

        Returns:
            Weather data dict with temperature, conditions, and alert info
        """
        if location_key not in self.LOCATIONS:
            logger.error(f"Unknown location: {location_key}")
            return None

        location = self.LOCATIONS[location_key]

        try:
            # Open-Meteo free API parameters
            params = {
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "timezone": location["timezone"],
                "daily": [
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "weathercode",
                    "precipitation_sum",
                    "precipitation_probability_max",
                    "windspeed_10m_max",
                ],
                "forecast_days": 7
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    params=params,
                    timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()

                    # Find the index for the target date
                    target_date_str = target_date.strftime("%Y-%m-%d")
                    try:
                        date_index = data["daily"]["time"].index(target_date_str)
                    except ValueError:
                        logger.warning(f"Date {target_date_str} not in forecast range")
                        return None

                    # Extract weather data for that date
                    daily = data["daily"]
                    temp_max = daily["temperature_2m_max"][date_index]
                    temp_min = daily["temperature_2m_min"][date_index]
                    weathercode = daily["weathercode"][date_index]
                    precipitation = daily["precipitation_sum"][date_index]
                    precip_probability = daily["precipitation_probability_max"][date_index]
                    windspeed = daily["windspeed_10m_max"][date_index]

                    # Interpret weather code
                    weather_description = self._interpret_weather_code(weathercode)

                    # Generate alert
                    alert = self._generate_alert(
                        temp_max=temp_max,
                        temp_min=temp_min,
                        weathercode=weathercode,
                        precipitation=precipitation,
                        precip_probability=precip_probability,
                        windspeed=windspeed,
                        weather_description=weather_description
                    )

                    return {
                        "location": location["name"],
                        "date": target_date_str,
                        "temperature_max": round(temp_max, 1),
                        "temperature_min": round(temp_min, 1),
                        "weather_description": weather_description,
                        "precipitation_mm": round(precipitation, 1),
                        "precipitation_probability": precip_probability,
                        "windspeed_kmh": round(windspeed, 1),
                        "alert": alert
                    }
                else:
                    logger.error(f"Open-Meteo API error: {response.status_code}")
                    return None

        except Exception as e:
            logger.error(f"Failed to fetch weather from Open-Meteo: {str(e)}", exc_info=True)
            return None

    async def get_alerts_for_all_locations(
        self,
        target_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Get weather alerts for both Dublin and Île de Ré for a specific date.

        Args:
            target_date: The date to get weather alerts for

        Returns:
            List of alert dicts (only locations with alerts are included)
        """
        alerts = []

        for location_key in self.LOCATIONS.keys():
            weather_data = await self.get_weather_for_date(location_key, target_date)

            if weather_data and weather_data.get("alert"):
                alerts.append(weather_data)

        return alerts

    def _interpret_weather_code(self, code: int) -> str:
        """
        Convert WMO weather code to human-readable description.

        Weather codes: https://open-meteo.com/en/docs
        """
        weather_codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            56: "Light freezing drizzle",
            57: "Dense freezing drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            66: "Light freezing rain",
            67: "Heavy freezing rain",
            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }
        return weather_codes.get(code, f"Unknown weather ({code})")

    def _generate_alert(
        self,
        temp_max: float,
        temp_min: float,
        weathercode: int,
        precipitation: float,
        precip_probability: int,
        windspeed: float,
        weather_description: str
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a weather alert based on conditions.

        Returns:
            Alert dict with type ("warning" or "info") and message, or None if no alert
        """
        alert_type = None
        reasons = []

        # Check for severe weather (warning level)
        if weathercode >= 95:  # Thunderstorms
            alert_type = "warning"
            reasons.append("⚡ Thunderstorms expected")

        elif weathercode in [65, 67, 75, 82, 86]:  # Heavy rain/snow
            alert_type = "warning"
            reasons.append(f"🌧️ Heavy precipitation: {weather_description}")

        elif weathercode in [66, 67, 56, 57]:  # Freezing rain
            alert_type = "warning"
            reasons.append("❄️ Freezing rain - dangerous travel conditions")

        elif temp_min < 0:
            alert_type = "warning" if not alert_type else alert_type
            reasons.append(f"🥶 Freezing temperatures: {round(temp_min)}°C")

        elif temp_max > 35:
            alert_type = "warning" if not alert_type else alert_type
            reasons.append(f"🔥 Extreme heat: {round(temp_max)}°C")

        # Check for moderate conditions (info level)
        elif weathercode in [61, 63, 71, 73, 80, 81]:  # Rain or snow
            alert_type = "info"
            reasons.append(f"🌦️ {weather_description}")

        elif windspeed > 50:
            alert_type = "info" if not alert_type else alert_type
            reasons.append(f"💨 Strong winds: {round(windspeed)} km/h")

        elif precip_probability >= 70:
            alert_type = "info" if not alert_type else alert_type
            reasons.append(f"☔ High chance of rain: {precip_probability}%")

        elif weathercode in [45, 48]:  # Fog
            alert_type = "info" if not alert_type else alert_type
            reasons.append("🌫️ Foggy conditions")

        # Return alert if any reasons were found
        if alert_type and reasons:
            return {
                "type": alert_type,
                "message": " • ".join(reasons)
            }

        return None
