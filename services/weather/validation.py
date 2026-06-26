"""Weather input validation.

Purpose: reject invalid Weather inputs before provider calls.
Responsibilities: validate city names, coordinates, units, and forecast days.
Dependencies: weather exceptions.
Extension Notes: add locale-specific city normalization later.
"""

from integrations.weather.errors import weather_error

VALID_UNITS = frozenset({"metric", "imperial"})


def city(value: str) -> str:
    """Validate and normalize a city name."""
    normalized = value.strip()
    if not normalized or len(normalized) > 120:
        raise weather_error("invalid_request", "City must be a non-empty value.", 400)
    return normalized


def units(value: str) -> str:
    """Validate Weather units."""
    if value not in VALID_UNITS:
        raise weather_error("invalid_request", "Units must be metric or imperial.", 400)
    return value


def forecast_days(value: int) -> int:
    """Validate forecast day count."""
    if value < 1 or value > 10:
        raise weather_error("invalid_request", "Forecast days must be between 1 and 10.", 400)
    return value


def coordinates(latitude: object, longitude: object) -> None:
    """Validate provider coordinates."""
    if not isinstance(latitude, int | float) or not isinstance(longitude, int | float):
        raise weather_error("invalid_request", "Weather coordinates are invalid.", 400)
    if latitude < -90 or latitude > 90 or longitude < -180 or longitude > 180:
        raise weather_error("invalid_request", "Weather coordinates are out of range.", 400)
