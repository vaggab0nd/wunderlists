"""
Unit tests for the OpenMeteoWeatherService
Tests weather code interpretation, alert generation, and location handling
"""
import pytest
from backend.app.services.open_meteo_weather import OpenMeteoWeatherService


class TestWeatherCodeInterpretation:
    """Tests for _interpret_weather_code method"""

    def setup_method(self):
        self.service = OpenMeteoWeatherService()

    def test_clear_sky(self):
        assert self.service._interpret_weather_code(0) == "Clear sky"

    def test_mainly_clear(self):
        assert self.service._interpret_weather_code(1) == "Mainly clear"

    def test_partly_cloudy(self):
        assert self.service._interpret_weather_code(2) == "Partly cloudy"

    def test_overcast(self):
        assert self.service._interpret_weather_code(3) == "Overcast"

    def test_foggy(self):
        assert self.service._interpret_weather_code(45) == "Foggy"

    def test_slight_rain(self):
        assert self.service._interpret_weather_code(61) == "Slight rain"

    def test_heavy_rain(self):
        assert self.service._interpret_weather_code(65) == "Heavy rain"

    def test_thunderstorm(self):
        assert self.service._interpret_weather_code(95) == "Thunderstorm"

    def test_thunderstorm_with_hail(self):
        assert self.service._interpret_weather_code(99) == "Thunderstorm with heavy hail"

    def test_slight_snow(self):
        assert self.service._interpret_weather_code(71) == "Slight snow"

    def test_heavy_snow(self):
        assert self.service._interpret_weather_code(75) == "Heavy snow"

    def test_unknown_code(self):
        result = self.service._interpret_weather_code(999)
        assert "Unknown weather" in result
        assert "999" in result


class TestAlertGeneration:
    """Tests for _generate_alert method"""

    def setup_method(self):
        self.service = OpenMeteoWeatherService()

    def test_thunderstorm_warning(self):
        """Test that thunderstorms generate a warning"""
        alert = self.service._generate_alert(
            temp_max=20, temp_min=15,
            weathercode=95, precipitation=10,
            precip_probability=90, windspeed=30,
            weather_description="Thunderstorm"
        )

        assert alert is not None
        assert alert["type"] == "warning"
        assert "Thunderstorms" in alert["message"]

    def test_heavy_rain_warning(self):
        """Test that heavy rain generates a warning"""
        alert = self.service._generate_alert(
            temp_max=15, temp_min=10,
            weathercode=65, precipitation=25,
            precip_probability=95, windspeed=20,
            weather_description="Heavy rain"
        )

        assert alert is not None
        assert alert["type"] == "warning"
        assert "Heavy precipitation" in alert["message"]

    def test_freezing_rain_warning(self):
        """Test that freezing rain generates a warning"""
        alert = self.service._generate_alert(
            temp_max=2, temp_min=-2,
            weathercode=66, precipitation=5,
            precip_probability=80, windspeed=15,
            weather_description="Light freezing rain"
        )

        assert alert is not None
        assert alert["type"] == "warning"
        assert "Freezing rain" in alert["message"]

    def test_freezing_temperature_warning(self):
        """Test that freezing temperatures generate a warning"""
        alert = self.service._generate_alert(
            temp_max=3, temp_min=-5,
            weathercode=0, precipitation=0,
            precip_probability=0, windspeed=10,
            weather_description="Clear sky"
        )

        assert alert is not None
        assert alert["type"] == "warning"
        assert "Freezing" in alert["message"]

    def test_extreme_heat_warning(self):
        """Test that extreme heat generates a warning"""
        alert = self.service._generate_alert(
            temp_max=40, temp_min=25,
            weathercode=0, precipitation=0,
            precip_probability=0, windspeed=5,
            weather_description="Clear sky"
        )

        assert alert is not None
        assert alert["type"] == "warning"
        assert "heat" in alert["message"].lower()

    def test_moderate_rain_info(self):
        """Test that moderate rain generates an info alert"""
        alert = self.service._generate_alert(
            temp_max=18, temp_min=12,
            weathercode=63, precipitation=5,
            precip_probability=75, windspeed=15,
            weather_description="Moderate rain"
        )

        assert alert is not None
        assert alert["type"] == "info"

    def test_fog_info(self):
        """Test that fog generates an info alert"""
        alert = self.service._generate_alert(
            temp_max=10, temp_min=5,
            weathercode=45, precipitation=0,
            precip_probability=10, windspeed=5,
            weather_description="Foggy"
        )

        assert alert is not None
        assert alert["type"] == "info"
        assert "Foggy" in alert["message"]

    def test_high_wind_info(self):
        """Test that strong winds generate an info alert"""
        alert = self.service._generate_alert(
            temp_max=15, temp_min=10,
            weathercode=2, precipitation=0,
            precip_probability=10, windspeed=55,
            weather_description="Partly cloudy"
        )

        assert alert is not None
        assert alert["type"] == "info"
        assert "winds" in alert["message"].lower()

    def test_high_precipitation_probability_info(self):
        """Test that high precip probability generates an info alert"""
        alert = self.service._generate_alert(
            temp_max=15, temp_min=10,
            weathercode=2, precipitation=0,
            precip_probability=80, windspeed=10,
            weather_description="Partly cloudy"
        )

        assert alert is not None
        assert alert["type"] == "info"
        assert "rain" in alert["message"].lower()

    def test_clear_weather_no_alert(self):
        """Test that clear, mild weather generates no alert"""
        alert = self.service._generate_alert(
            temp_max=22, temp_min=15,
            weathercode=0, precipitation=0,
            precip_probability=5, windspeed=10,
            weather_description="Clear sky"
        )

        assert alert is None

    def test_mild_partly_cloudy_no_alert(self):
        """Test that partly cloudy with mild temps generates no alert"""
        alert = self.service._generate_alert(
            temp_max=20, temp_min=12,
            weathercode=2, precipitation=0,
            precip_probability=20, windspeed=15,
            weather_description="Partly cloudy"
        )

        assert alert is None


class TestLocationConfiguration:
    """Tests for hardcoded location configuration"""

    def setup_method(self):
        self.service = OpenMeteoWeatherService()

    def test_dublin_location_exists(self):
        """Test Dublin is configured"""
        assert "Dublin" in self.service.LOCATIONS
        dublin = self.service.LOCATIONS["Dublin"]
        assert dublin["latitude"] == 53.3498
        assert dublin["longitude"] == -6.2603

    def test_ile_de_re_location_exists(self):
        """Test Île de Ré is configured"""
        assert "Île de Ré" in self.service.LOCATIONS
        ile = self.service.LOCATIONS["Île de Ré"]
        assert ile["latitude"] == 46.2
        assert ile["longitude"] == -1.4

    def test_exactly_two_locations(self):
        """Test that exactly two locations are configured"""
        assert len(self.service.LOCATIONS) == 2
