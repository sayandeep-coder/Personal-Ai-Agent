"""Weather API routes.

Purpose: expose read-only Weather context endpoints.
Responsibilities: validate query parameters and delegate to WeatherService.
Dependencies: FastAPI, response envelope, and Weather factory.
Extension Notes: add coordinates endpoints without changing provider contracts.
"""

from fastapi import APIRouter, Query
from time import perf_counter

from apps.api.responses import success
from apps.api.schemas.weather import WeatherUnits
from services.weather.factory import create_weather_service

router = APIRouter(prefix="/weather", tags=["weather"])


def current(city: str = Query(..., min_length=1), country: str | None = None, units: WeatherUnits = WeatherUnits.METRIC) -> dict[str, object]:
    """Return current weather for a city."""
    started = perf_counter()
    data = create_weather_service().current(city, country, units.value)
    return success(data, _meta(started, units.value))


def forecast(city: str = Query(..., min_length=1), days: int = Query(5, ge=1, le=10), units: WeatherUnits = WeatherUnits.METRIC) -> dict[str, object]:
    """Return daily weather forecast."""
    started = perf_counter()
    data = create_weather_service().forecast(city, days, units.value)
    return success(data, _meta(started, units.value) | {"days": days})


def hourly(city: str = Query(..., min_length=1), units: WeatherUnits = WeatherUnits.METRIC) -> dict[str, object]:
    """Return hourly weather forecast."""
    started = perf_counter()
    data = create_weather_service().hourly(city, units.value)
    return success(data, _meta(started, units.value))


def air_quality(city: str = Query(..., min_length=1)) -> dict[str, object]:
    """Return air quality for a city."""
    started = perf_counter()
    data = create_weather_service().air_quality(city)
    return success(data, _meta(started, "metric"))


def uv(city: str = Query(..., min_length=1), units: WeatherUnits = WeatherUnits.METRIC) -> dict[str, object]:
    """Return UV index for a city."""
    started = perf_counter()
    data = create_weather_service().uv(city, units.value)
    return success(data, _meta(started, units.value))


def alerts(city: str = Query(..., min_length=1), units: WeatherUnits = WeatherUnits.METRIC) -> dict[str, object]:
    """Return active weather alerts for a city."""
    started = perf_counter()
    data = create_weather_service().alerts(city, units.value)
    return success(data, _meta(started, units.value))


router.add_api_route("/current", current, methods=["GET"])
router.add_api_route("/forecast", forecast, methods=["GET"])
router.add_api_route("/hourly", hourly, methods=["GET"])
router.add_api_route("/air-quality", air_quality, methods=["GET"])
router.add_api_route("/uv", uv, methods=["GET"])
router.add_api_route("/alerts", alerts, methods=["GET"])


def _meta(started: float, units: str) -> dict[str, object]:
    """Return Weather response metadata."""
    return {"provider": "openweather", "units": units, "cached": False, "response_time_ms": round((perf_counter() - started) * 1000)}
