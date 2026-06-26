"""OpenWeather provider adapter.

Purpose: encapsulate provider-specific Weather API calls.
Responsibilities: geocode locations and call weather data endpoints.
Dependencies: settings, transport, and weather exceptions.
Extension Notes: add alternate providers behind the same service contract.
"""

from pydantic import SecretStr

from core.config import Settings
from integrations.weather.errors import weather_error
from integrations.weather.transport import JsonDict, JsonPayload, WeatherTransport


class OpenWeatherProvider:
    """OpenWeather-backed weather provider."""

    def __init__(self, settings: Settings, transport: WeatherTransport) -> None:
        """Create provider from settings and transport."""
        self._api_key = _api_key(settings.weather_api_key)
        self._transport = transport

    def current(self, city: str, country: str | None, units: str) -> JsonDict:
        """Return current weather raw provider payload."""
        location = self.location(city, country)
        return {
            "location": location,
            "weather": self._get("/data/2.5/weather", _coords(location) | {"units": units}),
        }

    def daily_forecast(self, city: str, days: int, units: str) -> JsonDict:
        """Return daily forecast raw provider payload."""
        location = self.location(city, None)
        data = self._get("/data/2.5/forecast", _coords(location) | {"units": units})
        return {"location": location, "weather": data, "days": days}

    def hourly_forecast(self, city: str, units: str) -> JsonDict:
        """Return hourly forecast raw provider payload."""
        location = self.location(city, None)
        data = self._get("/data/2.5/forecast", _coords(location) | {"units": units})
        return {"location": location, "weather": data}

    def air_quality(self, city: str) -> JsonDict:
        """Return air quality raw provider payload."""
        location = self.location(city, None)
        return {"location": location, "weather": self._get("/data/2.5/air_pollution", _coords(location))}

    def one_call(self, city: str, units: str, exclude: str = "minutely,hourly,daily") -> JsonDict:
        """Return One Call raw provider payload."""
        location = self.location(city, None)
        return {"location": location, "weather": self._one_call(location, units, exclude)}

    def location(self, city: str, country: str | None) -> JsonDict:
        """Resolve city into provider coordinates."""
        query = f"{city},{country}" if country else city
        results = self._request("/geo/1.0/direct", {"q": query, "limit": 1})
        if not isinstance(results, list) or not results:
            raise weather_error("not_found", "Weather location was not found.", 404)
        first = results[0]
        return dict(first) if isinstance(first, dict) else {}

    def _one_call(self, location: JsonDict, units: str, exclude: str) -> JsonDict:
        """Return One Call payload for a resolved location."""
        return self._get("/data/3.0/onecall", _coords(location) | {"units": units, "exclude": exclude})

    def _get(self, path: str, params: dict[str, object]) -> JsonDict:
        """Execute provider GET with API key."""
        payload = self._request(path, params)
        if not isinstance(payload, dict):
            raise weather_error("provider_error", "Weather provider returned invalid data.", 500)
        return payload

    def _request(self, path: str, params: dict[str, object]) -> JsonPayload:
        """Execute provider GET with API key."""
        return self._transport.get(path, params | {"appid": self._api_key})


def _api_key(value: SecretStr | None) -> str:
    """Return configured Weather API key."""
    if value is None:
        raise weather_error("invalid_key", "Weather API key is not configured.", 401)
    return value.get_secret_value()


def _coords(location: JsonDict) -> dict[str, object]:
    """Return latitude/longitude params from geocoded location."""
    return {"lat": location.get("lat"), "lon": location.get("lon")}
