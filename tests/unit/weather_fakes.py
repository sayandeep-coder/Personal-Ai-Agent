"""Weather test fakes.

Purpose: provide deterministic Weather provider responses.
Responsibilities: simulate success and provider failures.
Dependencies: weather JSON alias and exception helpers.
Extension Notes: add more provider edge cases as normalizers expand.
"""

from integrations.weather.errors import weather_error
from integrations.weather.transport import JsonDict


class WeatherProvider:
    """Fake Weather provider."""

    def __init__(self, mode: str = "ok") -> None:
        """Create fake provider."""
        self.mode = mode

    def current(self, city: str, country: str | None, units: str) -> JsonDict:
        """Return current payload."""
        self._raise()
        lat = 999 if self.mode == "bad_coords" else 22.57
        return {"location": {"name": city, "lat": lat, "lon": 88.36}, "weather": _current()}

    def daily_forecast(self, city: str, days: int, units: str) -> JsonDict:
        """Return forecast payload."""
        return {"location": _loc(city), "days": days, "weather": {"list": [_forecast()]}}

    def hourly_forecast(self, city: str, units: str) -> JsonDict:
        """Return hourly payload."""
        return {"location": _loc(city), "weather": {"list": [_forecast()]}}

    def air_quality(self, city: str) -> JsonDict:
        """Return air quality payload."""
        return {"location": _loc(city), "weather": {"list": [{"main": {"aqi": 2}, "components": {"pm2_5": 1}}]}}

    def one_call(self, city: str, units: str, exclude: str = "minutely,hourly,daily") -> JsonDict:
        """Return one-call payload."""
        return {"location": _loc(city), "weather": {"current": {"uvi": 4.2}, "alerts": []}}

    def _raise(self) -> None:
        if self.mode == "timeout":
            raise weather_error("timeout", "Weather provider timed out.", 503)
        if self.mode == "rate":
            raise weather_error("rate_limited", "Weather provider rate limit exceeded.", 429)
        if self.mode == "key":
            raise weather_error("invalid_key", "Weather API key is invalid.", 401)
        if self.mode == "down":
            raise weather_error("unavailable", "Weather provider is unavailable.", 503)


def _loc(city: str) -> JsonDict:
    return {"name": city, "lat": 22.57, "lon": 88.36}


def _current() -> JsonDict:
    return {"main": {"temp": 30, "feels_like": 32, "humidity": 70}, "weather": [{"main": "Clouds"}]}


def _forecast() -> JsonDict:
    return {"dt": 1, "dt_txt": "2026-06-30 12:00:00", "main": {"temp": 30, "humidity": 60}, "weather": [{"main": "Clouds", "description": "broken clouds"}]}
