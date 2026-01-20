# Weather Alerts Integration - Open-Meteo

## Overview

This integration provides **weather alerts for travel days** using the free Open-Meteo API. No API key is required!

Weather is monitored for two hardcoded locations:
- **Dublin, Ireland** (53.3498°N, 6.2603°W)
- **Île de Ré, France** (46.2°N, 1.4°W)

## Features

✅ **No API key needed** - Open-Meteo is completely free
✅ **7-day forecast** - Check weather up to 14 days ahead
✅ **Smart alerts** - Categorizes weather as "warning" or "info"
✅ **30+ weather conditions** - Rain, snow, fog, thunderstorms, extreme temps
✅ **Travel day tracking** - Tasks can be marked with `is_travel_day: true`
✅ **Temperature in Celsius** - Matches European standards

## API Endpoints

### 1. Get Weather Alerts

```http
GET /api/weather/alerts?days_ahead=7
```

Returns weather alerts for all tasks marked as travel days in the next N days.

**Response:**
```json
{
  "alerts": [
    {
      "task": {
        "id": 1,
        "title": "Trip to Dublin",
        "due_date": "2026-01-25T00:00:00Z",
        "priority": "high"
      },
      "weather": {
        "Dublin, Ireland": {
          "location": "Dublin, Ireland",
          "date": "2026-01-25",
          "temperature_max": 8.5,
          "temperature_min": 3.2,
          "weather_description": "Moderate rain",
          "precipitation_mm": 12.3,
          "precipitation_probability": 85,
          "windspeed_kmh": 32.1,
          "alert": {
            "type": "info",
            "message": "🌦️ Moderate rain • ☔ High chance of rain: 85%"
          }
        },
        "Île de Ré, France": {
          "location": "Île de Ré, France",
          "date": "2026-01-25",
          "temperature_max": 12.1,
          "temperature_min": 6.8,
          "weather_description": "Partly cloudy",
          "precipitation_mm": 0.2,
          "precipitation_probability": 20,
          "windspeed_kmh": 18.5,
          "alert": null
        }
      }
    }
  ],
  "summary": {
    "total_alerts": 2,
    "warning_count": 0,
    "info_count": 2,
    "travel_days_checked": 3,
    "date_range": {
      "from": "2026-01-20",
      "to": "2026-01-27"
    }
  }
}
```

### 2. Refresh Weather Data

```http
GET /api/weather/refresh?days_ahead=7
```

Manually trigger a weather data refresh. Returns same format as `/alerts` with additional metadata.

### 3. Test Weather Service

```http
GET /api/weather/test
```

Test endpoint to verify Open-Meteo API is working. Returns tomorrow's weather for both locations.

### 4. Get Monitored Locations

```http
GET /api/weather/locations
```

Returns information about the hardcoded locations being monitored.

## Alert Types

### ⚠️ Warning Level
- ⚡ Thunderstorms
- 🌧️ Heavy rain or snow
- ❄️ Freezing rain
- 🥶 Freezing temperatures (< 0°C)
- 🔥 Extreme heat (> 35°C)

### ℹ️ Info Level
- 🌦️ Light to moderate rain/snow
- 💨 Strong winds (> 50 km/h)
- ☔ High precipitation probability (≥ 70%)
- 🌫️ Foggy conditions

## Database Schema Changes

### Task Model
Added `is_travel_day` boolean field to the `tasks` table:

```python
class Task(Base):
    # ... existing fields ...
    is_travel_day = Column(Boolean, default=False)
```

### Creating Travel Day Tasks

**API Request:**
```http
POST /api/tasks/
Content-Type: application/json

{
  "title": "Business trip to Dublin",
  "description": "Meeting with clients",
  "due_date": "2026-01-25T09:00:00Z",
  "is_travel_day": true,
  "priority": "high"
}
```

**Updating Existing Task:**
```http
PATCH /api/tasks/{task_id}
Content-Type: application/json

{
  "is_travel_day": true
}
```

## Migration

A database migration is included to add the `is_travel_day` field:

```bash
# Migration will run automatically on app startup
# Or run manually with:
alembic upgrade head
```

**Migration file:** `backend/alembic/versions/002_add_is_travel_day_to_tasks.py`

## Implementation Files

```
backend/
├── app/
│   ├── models/
│   │   └── task.py                          # Updated with is_travel_day field
│   ├── schemas/
│   │   └── task.py                          # Updated schemas
│   ├── routes/
│   │   └── weather_alerts.py                # New: Weather alert endpoints
│   ├── services/
│   │   └── open_meteo_weather.py            # New: Open-Meteo integration
│   └── main.py                              # Updated: Register weather_alerts router
└── alembic/
    └── versions/
        └── 002_add_is_travel_day_to_tasks.py # New migration
```

## How It Works

1. **Mark tasks as travel days**: Set `is_travel_day: true` on tasks that involve travel
2. **Set due dates**: Ensure travel day tasks have `due_date` set
3. **Call `/api/weather/alerts`**: Frontend fetches alerts for upcoming travel days
4. **Display alerts**: Show weather warnings/info to user

## Frontend Integration

Your frontend at https://github.com/vaggab0nd/your-digital-hub is already configured to consume these endpoints.

Once deployed to Railway, the weather alerts will automatically appear in your dashboard!

## Weather Codes Reference

Open-Meteo uses WMO weather codes. Here are the most common:

- **0**: Clear sky
- **1-3**: Cloudy (mainly clear → overcast)
- **45-48**: Fog
- **51-57**: Drizzle (light → freezing)
- **61-67**: Rain (slight → heavy freezing)
- **71-77**: Snow (slight → heavy)
- **80-82**: Rain showers
- **85-86**: Snow showers
- **95-99**: Thunderstorms (with optional hail)

## Dependencies

All required dependencies are already in `requirements.txt`:
- `httpx==0.26.0` - For async HTTP requests

No additional packages needed!

## Testing

### Local Testing
```bash
# Start the server
uvicorn backend.app.main:app --reload

# Test the weather service
curl http://localhost:8000/api/weather/test

# Get locations info
curl http://localhost:8000/api/weather/locations

# Create a test travel day task
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test travel day",
    "due_date": "2026-01-25T10:00:00Z",
    "is_travel_day": true
  }'

# Get weather alerts
curl http://localhost:8000/api/weather/alerts?days_ahead=7
```

### Railway Deployment

After pushing to Railway:
```bash
# Check health
curl https://your-app.up.railway.app/health

# Test weather
curl https://your-app.up.railway.app/api/weather/test

# Get alerts
curl https://your-app.up.railway.app/api/weather/alerts
```

## Customization

### Change Monitored Locations

Edit `backend/app/services/open_meteo_weather.py`:

```python
LOCATIONS = {
    "Your City": {
        "name": "Your City, Country",
        "latitude": 12.345,
        "longitude": 67.890,
        "timezone": "Europe/YourCity"
    }
}
```

### Adjust Alert Thresholds

Modify `_generate_alert()` method in `open_meteo_weather.py`:

```python
# Example: Lower the strong wind threshold
if windspeed > 40:  # Changed from 50
    alert_type = "info"
    reasons.append(f"💨 Strong winds: {round(windspeed)} km/h")
```

## API Documentation

Once deployed, visit:
- **Swagger UI**: `https://your-app.up.railway.app/docs`
- **ReDoc**: `https://your-app.up.railway.app/redoc`

## Troubleshooting

### No alerts returned
- Check that tasks have `is_travel_day: true`
- Verify tasks have `due_date` set
- Ensure `due_date` is within the next 7 days
- Check tasks are not completed (`is_completed: false`)

### Open-Meteo API errors
- Open-Meteo is free and has no rate limits
- If API is down, check https://open-meteo.com/
- Timeout is set to 10 seconds per request

### Migration not running
- Check Railway logs: `railway logs`
- Verify DATABASE_URL is set
- Migration runs automatically on startup
- Can also run manually: `alembic upgrade head`

## Credits

- **Weather Data**: [Open-Meteo](https://open-meteo.com/) - Free Weather API
- **Weather Codes**: WMO (World Meteorological Organization)
- **Built for**: Wunderlists Task Management App

---

**Ready to deploy!** 🚀

Push to Railway and your frontend will automatically start displaying weather alerts.
