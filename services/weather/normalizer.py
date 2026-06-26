"""Weather response normalization.

Purpose: convert provider payloads into stable Weather contracts.
Responsibilities: normalize current, forecast, hourly, AQI, UV, and alerts.
Dependencies: provider JSON shapes.
Extension Notes: add provider confidence metadata if multiple providers exist.
"""

from integrations.weather.transport import JsonDict
from services.weather.current import current_weather
from services.weather.forecast import daily_from_list, hourly_from_list
from services.weather.items import alert_item, as_dict, daily_item, first, hour_item
from services.weather.items import uv_advice, uv_risk


def current(payload: JsonDict, units: str = "metric") -> dict[str, object]:
    """Return normalized current weather."""
    return current_weather(payload, units)


def daily(payload: JsonDict, units: str = "metric") -> dict[str, object]:
    """Return normalized daily forecast."""
    raw_days = payload.get("days", 1)
    days = int(raw_days) if isinstance(raw_days, int | str) else 1
    items = _data(payload).get("daily", [])
    items = items if isinstance(items, list) else []
    if not items:
        source = _data(payload).get("list", [])
        return _base(payload) | {"forecast": daily_from_list(source if isinstance(source, list) else [], days, units)}
    return _base(payload) | {"forecast": [daily_item(item, units) for item in items[:days] if isinstance(item, dict)]}


def hourly(payload: JsonDict) -> dict[str, object]:
    """Return normalized hourly forecast."""
    items = _data(payload).get("hourly", [])
    items = items if isinstance(items, list) else []
    if not items:
        source = _data(payload).get("list", [])
        return _base(payload) | {"hours": hourly_from_list(source if isinstance(source, list) else [])}
    return _base(payload) | {"hours": [hour_item(item) for item in items[:24] if isinstance(item, dict)]}


def air_quality(payload: JsonDict) -> dict[str, object]:
    """Return normalized air quality."""
    item = first(_data(payload).get("list"))
    components = as_dict(item.get("components"))
    return _base(payload) | {"aqi": as_dict(item.get("main")).get("aqi"), **{key: components.get(key) for key in ("pm2_5", "pm10", "co", "no2", "so2", "o3")}}


def uv(payload: JsonDict) -> dict[str, object]:
    """Return normalized UV index."""
    raw_index = as_dict(_data(payload).get("current")).get("uvi", _data(payload).get("uvi", 0))
    index = float(raw_index) if isinstance(raw_index, int | float | str) else 0.0
    return _base(payload) | {"uv_index": index, "risk_level": uv_risk(index), "recommendation": uv_advice(index)}


def alerts(payload: JsonDict) -> dict[str, object]:
    """Return normalized weather alerts."""
    items = _data(payload).get("alerts", [])
    items = items if isinstance(items, list) else []
    return _base(payload) | {"alerts": [alert_item(item) for item in items if isinstance(item, dict)]}


def _base(payload: JsonDict) -> dict[str, object]:
    loc = as_dict(payload.get("location"))
    return {"location": loc.get("name"), "coordinates": {"latitude": loc.get("lat"), "longitude": loc.get("lon")}}


def _data(payload: JsonDict) -> JsonDict:
    return as_dict(payload.get("weather"))
