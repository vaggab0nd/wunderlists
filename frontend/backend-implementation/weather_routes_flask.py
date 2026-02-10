"""
Flask routes for weather endpoints
Add these routes to your Flask application
"""
from flask import Blueprint, jsonify
from datetime import datetime
import uuid
import asyncio
from .weather_service import get_weather_alerts_for_today

weather_bp = Blueprint('weather', __name__, url_prefix='/api/weather')


def run_async(coro):
    """Helper to run async functions in Flask"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@weather_bp.route('/alerts', methods=['GET'])
def get_weather_alerts():
    """
    Get all weather alerts for today
    Returns weather information for Dublin and Île de Ré
    """
    try:
        # Fetch fresh weather data
        alerts = run_async(get_weather_alerts_for_today())

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

        return jsonify(formatted_alerts), 200

    except Exception as e:
        return jsonify({"error": f"Failed to fetch weather alerts: {str(e)}"}), 500


@weather_bp.route('/refresh', methods=['POST'])
def refresh_weather_alerts():
    """
    Manually refresh weather data
    This endpoint triggers a fresh fetch from Open-Meteo
    """
    try:
        alerts = run_async(get_weather_alerts_for_today())

        return jsonify({
            "success": True,
            "message": f"Successfully refreshed weather data for {len(alerts)} locations",
            "timestamp": datetime.now().isoformat(),
            "locations_updated": [alert["location"] for alert in alerts]
        }), 200

    except Exception as e:
        return jsonify({"error": f"Failed to refresh weather alerts: {str(e)}"}), 500


# To use these routes, add this to your main Flask app:
# from .weather_routes_flask import weather_bp
# app.register_blueprint(weather_bp)
