"""Weather service tests.

Purpose: verify Weather service normalization and failures.
Responsibilities: cover endpoint use cases and provider error propagation.
Dependencies: pytest, WeatherService, and fakes.
Extension Notes: add live provider contract tests only with sandbox keys.
"""

import pytest

from core.exceptions import ValidationException
from services.weather.service import WeatherService
from tests.unit.weather_fakes import WeatherProvider


def test_current_weather() -> None:
    """Current weather is normalized."""
    result = WeatherService(WeatherProvider()).current("Kolkata", None, "metric")
    assert result["location"] == "Kolkata"
    temperature = result["temperature"]
    wind = result["wind"]
    weather = result["weather"]
    assert isinstance(temperature, dict)
    assert isinstance(wind, dict)
    assert isinstance(weather, dict)
    assert temperature == {"current": 30, "feels_like": 32, "unit": "°C"}
    assert wind["unit"] == "m/s"
    assert weather["icon_url"] is None


def test_forecast_hourly_air_quality_uv_alerts() -> None:
    """Weather endpoints return normalized payloads."""
    service = WeatherService(WeatherProvider())
    forecast = service.forecast("Kolkata", 1, "metric")["forecast"]
    assert isinstance(forecast, list)
    assert isinstance(forecast[0], dict)
    assert forecast[0]["temperature"] == {"min": 30.0, "max": 30.0, "unit": "°C"}
    assert forecast[0]["description"] == "broken clouds"
    assert "summary" in forecast[0]
    assert service.hourly("Kolkata", "metric")["hours"]
    assert service.air_quality("Kolkata")["aqi"] == 2
    assert service.uv("Kolkata", "metric")["risk_level"] == "low"
    assert service.alerts("Kolkata", "metric")["alerts"] == []


def test_invalid_city_and_coordinates() -> None:
    """Invalid inputs fail before successful responses."""
    with pytest.raises(ValidationException):
        WeatherService(WeatherProvider()).current("", None, "metric")
    with pytest.raises(ValidationException):
        WeatherService(WeatherProvider("bad_coords")).current("Kolkata", None, "metric")


@pytest.mark.parametrize(("mode", "status"), [("timeout", 503), ("down", 503), ("rate", 429), ("key", 401)])
def test_provider_failures(mode: str, status: int) -> None:
    """Provider failures preserve safe status hints."""
    with pytest.raises(ValidationException) as exc:
        WeatherService(WeatherProvider(mode)).current("Kolkata", None, "metric")
    assert exc.value.details["status_code"] == status


def test_invalid_forecast_days_and_units() -> None:
    """Invalid forecast days and units are rejected."""
    service = WeatherService(WeatherProvider())
    with pytest.raises(ValidationException):
        service.forecast("Kolkata", 11, "metric")
    with pytest.raises(ValidationException):
        service.current("Kolkata", None, "kelvin")
