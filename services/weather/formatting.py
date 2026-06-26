"""Weather formatting helpers.

Purpose: format Weather units, directions, timestamps, and summaries.
Responsibilities: keep presentation shaping out of provider code.
Dependencies: datetime standard library.
Extension Notes: add localization when user preferences are available.
"""

from datetime import UTC, datetime, timedelta, timezone


def epoch(value: object, offset: object = 0) -> str | None:
    """Return an ISO timestamp from epoch seconds and timezone offset."""
    if not isinstance(value, int | float):
        return None
    seconds = int(offset) if isinstance(offset, int | float) else 0
    tz = timezone(timedelta(seconds=seconds))
    return datetime.fromtimestamp(value, UTC).astimezone(tz).isoformat()


def temp_unit(units: str) -> str:
    """Return temperature unit label."""
    return "°F" if units == "imperial" else "°C"


def wind_unit(units: str) -> str:
    """Return wind speed unit label."""
    return "mph" if units == "imperial" else "m/s"


def direction_text(degrees: object) -> str | None:
    """Return compass direction text."""
    if not isinstance(degrees, int | float):
        return None
    labels = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    return labels[round(float(degrees) / 45) % 8]


def icon_url(icon: object) -> str | None:
    """Return OpenWeather icon URL."""
    return f"https://openweathermap.org/img/wn/{icon}@2x.png" if icon else None


def summary(temp: object, description: object) -> dict[str, str]:
    """Return human summary and recommendation."""
    condition = f"Weather with {description}."
    if isinstance(temp, int | float) and temp >= 30:
        condition = f"Warm with {description}."
    return {"condition": condition, "recommendation": _recommendation(temp)}


def _recommendation(temp: object) -> str:
    """Return a simple weather recommendation."""
    if isinstance(temp, int | float) and temp >= 30:
        return "Carry water if spending extended time outdoors."
    return "Check conditions before extended outdoor plans."
