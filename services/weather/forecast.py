"""OpenWeather forecast list normalization.

Purpose: adapt 3-hour forecast entries into daily and hourly contracts.
Responsibilities: aggregate daily min/max values and map hourly fields.
Dependencies: Weather item helpers.
Extension Notes: improve day bucketing with timezone-aware local dates later.
"""

from integrations.weather.transport import JsonDict
from services.weather.forecast_items import first_weather, forecast_day


def daily_from_list(items: list[object], days: int, units: str) -> list[dict[str, object]]:
    """Return daily forecasts from OpenWeather 3-hour entries."""
    grouped: dict[str, list[JsonDict]] = {}
    for item in items:
        if isinstance(item, dict):
            key = str(item.get("dt_txt", item.get("dt", "")))[:10]
            grouped.setdefault(key, []).append(item)
    return [_daily(key, values, units) for key, values in list(grouped.items())[:days]]


def hourly_from_list(items: list[object]) -> list[dict[str, object]]:
    """Return hourly forecasts from OpenWeather 3-hour entries."""
    return [_hour(item) for item in items[:24] if isinstance(item, dict)]


def _daily(day: str, values: list[JsonDict], units: str) -> dict[str, object]:
    """Return one daily aggregate."""
    temps = [_main(item).get("temp") for item in values]
    numeric = [float(value) for value in temps if isinstance(value, int | float | str)]
    first_item = values[0] if values else {}
    return forecast_day(
        day,
        min(numeric) if numeric else None,
        max(numeric) if numeric else None,
        _main(first_item).get("humidity"),
        first_item.get("pop"),
        first_weather(first_item),
        units,
    )


def _hour(item: JsonDict) -> dict[str, object]:
    """Return one hourly forecast."""
    weather = first_weather(item)
    wind = item.get("wind", {})
    return {
        "hour": item.get("dt"),
        "temperature": _main(item).get("temp"),
        "feels_like": _main(item).get("feels_like"),
        "humidity": _main(item).get("humidity"),
        "wind": {"speed": wind.get("speed") if isinstance(wind, dict) else None},
        "rain_probability": item.get("pop"),
        "condition": weather.get("main"),
    }


def _main(item: JsonDict) -> JsonDict:
    """Return forecast main block."""
    value = item.get("main", {})
    return dict(value) if isinstance(value, dict) else {}
