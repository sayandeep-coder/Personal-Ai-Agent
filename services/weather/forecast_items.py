"""Weather forecast item formatting.

Purpose: build final daily forecast response items.
Responsibilities: nest temperatures, include descriptions, and summarize days.
Dependencies: weather formatting and JSON helpers.
Extension Notes: add sunrise/sunset when provider data is available.
"""

from integrations.weather.transport import JsonDict
from services.weather.formatting import temp_unit


def forecast_day(
    date: object,
    min_temp: object,
    max_temp: object,
    humidity: object,
    pop: object,
    weather: JsonDict,
    units: str,
) -> dict[str, object]:
    """Return one daily forecast item."""
    return {
        "date": date,
        "temperature": {"min": min_temp, "max": max_temp, "unit": temp_unit(units)},
        "humidity": humidity,
        "precipitation_probability": pop,
        "condition": weather.get("main"),
        "description": weather.get("description"),
        "icon": weather.get("icon"),
        "summary": _summary(max_temp, weather.get("description")),
    }


def first_weather(item: JsonDict) -> JsonDict:
    """Return first weather condition from a forecast item."""
    value = item.get("weather")
    return dict(value[0]) if isinstance(value, list) and value and isinstance(value[0], dict) else {}


def _summary(max_temp: object, description: object) -> dict[str, str]:
    """Return daily forecast summary."""
    text = str(description or "available conditions")
    condition = f"Mostly {text}."
    recommendation = "Light outdoor activities are suitable."
    if isinstance(max_temp, int | float) and max_temp >= 30:
        recommendation = "Expect warm temperatures. Carry water for outdoor plans."
    return {"condition": condition, "recommendation": recommendation}
