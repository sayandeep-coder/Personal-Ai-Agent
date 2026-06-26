"""Weather normalized item builders.

Purpose: build normalized Weather forecast, hourly, alert, and UV fragments.
Responsibilities: keep item-level shaping separate from aggregate responses.
Dependencies: Weather JSON alias.
Extension Notes: add localized text recommendations here later.
"""

from integrations.weather.transport import JsonDict
from services.weather.forecast_items import forecast_day


def daily_item(item: JsonDict, units: str) -> dict[str, object]:
    """Return a normalized daily forecast item."""
    temp = as_dict(item.get("temp"))
    weather = first(item.get("weather"))
    return forecast_day(item.get("dt"), temp.get("min"), temp.get("max"), item.get("humidity"), item.get("pop"), weather, units)


def hour_item(item: JsonDict) -> dict[str, object]:
    """Return a normalized hourly forecast item."""
    weather = first(item.get("weather"))
    return {
        "hour": item.get("dt"),
        "temperature": item.get("temp"),
        "feels_like": item.get("feels_like"),
        "humidity": item.get("humidity"),
        "wind": {"speed": item.get("wind_speed"), "direction": item.get("wind_deg")},
        "rain_probability": item.get("pop"),
        "condition": weather.get("main"),
    }


def alert_item(item: JsonDict) -> dict[str, object]:
    """Return a normalized weather alert."""
    return {
        "title": item.get("event"),
        "severity": item.get("severity", "unknown"),
        "description": item.get("description"),
        "start_time": item.get("start"),
        "end_time": item.get("end"),
    }


def uv_risk(index: float) -> str:
    """Return UV risk level."""
    if index < 3:
        return "low"
    if index < 6:
        return "moderate"
    if index < 8:
        return "high"
    return "very_high" if index < 11 else "extreme"


def uv_advice(index: float) -> str:
    """Return UV protection recommendation."""
    if index < 3:
        return "Minimal protection required."
    if index < 8:
        return "Use sunscreen and seek shade during midday."
    return "Avoid midday sun and use strong sun protection."


def as_dict(value: object) -> JsonDict:
    """Return value as dictionary when possible."""
    return dict(value) if isinstance(value, dict) else {}


def first(value: object) -> JsonDict:
    """Return first list dictionary when available."""
    return as_dict(value[0]) if isinstance(value, list) and value and isinstance(value[0], dict) else {}
