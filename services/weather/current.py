"""Current weather normalization.

Purpose: shape current weather into the public API contract.
Responsibilities: format nested temperature, pressure, visibility, wind, and weather.
Dependencies: weather formatting and item helpers.
Extension Notes: add localized summary rules when user preferences exist.
"""

from integrations.weather.transport import JsonDict
from services.weather.formatting import direction_text, epoch, icon_url, summary
from services.weather.formatting import temp_unit, wind_unit
from services.weather.items import as_dict, first


def current_weather(payload: JsonDict, units: str = "metric") -> dict[str, object]:
    """Return normalized current weather."""
    data = as_dict(payload.get("weather"))
    sys = as_dict(data.get("sys"))
    wind = as_dict(data.get("wind"))
    main = as_dict(data.get("main"))
    weather = first(data.get("weather"))
    offset = data.get("timezone", 0)
    temp = main.get("temp")
    description = weather.get("description")
    return _base(payload) | {
        "temperature": {"current": temp, "feels_like": main.get("feels_like"), "unit": temp_unit(units)},
        "humidity": main.get("humidity"),
        "pressure": {"value": main.get("pressure"), "unit": "hPa"},
        "visibility": _visibility(data.get("visibility")),
        "wind": _wind(wind, units),
        "weather": _weather(weather),
        "sunrise": epoch(sys.get("sunrise"), offset),
        "sunset": epoch(sys.get("sunset"), offset),
        "observation_time": epoch(data.get("dt"), offset),
        "summary": summary(temp, description),
    }


def _base(payload: JsonDict) -> dict[str, object]:
    loc = as_dict(payload.get("location"))
    return {"location": loc.get("name"), "coordinates": {"latitude": loc.get("lat"), "longitude": loc.get("lon")}}


def _visibility(value: object) -> dict[str, object]:
    meters = value if isinstance(value, int | float) else None
    return {"meters": meters, "kilometers": round(meters / 1000, 2) if meters is not None else None}


def _wind(wind: JsonDict, units: str) -> dict[str, object]:
    degrees = wind.get("deg")
    return {"speed": wind.get("speed"), "unit": wind_unit(units), "direction": degrees, "direction_text": direction_text(degrees)}


def _weather(weather: JsonDict) -> dict[str, object]:
    icon = weather.get("icon")
    return {"condition": weather.get("main"), "description": weather.get("description"), "icon": icon, "icon_url": icon_url(icon)}
