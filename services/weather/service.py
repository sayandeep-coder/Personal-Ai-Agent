"""Weather service.

Purpose: provide normalized environmental context to API and CLI callers.
Responsibilities: validate inputs, call provider, normalize data, and log status.
Dependencies: Weather provider, normalizers, validation, and logging.
Extension Notes: add caching here when weather usage becomes frequent.
"""

from collections.abc import Callable
from time import perf_counter
from typing import Protocol

from integrations.weather.transport import JsonDict
from core.logging import get_logger
from services.weather import normalizer
from services.weather.validation import city as validate_city
from services.weather.validation import coordinates, forecast_days, units as validate_units

logger = get_logger(__name__)


class WeatherProviderPort(Protocol):
    """Protocol-like base for Weather providers."""

    def current(self, city: str, country: str | None, units: str) -> JsonDict: ...
    def daily_forecast(self, city: str, days: int, units: str) -> JsonDict: ...
    def hourly_forecast(self, city: str, units: str) -> JsonDict: ...
    def air_quality(self, city: str) -> JsonDict: ...
    def one_call(self, city: str, units: str, exclude: str = "minutely,hourly,daily") -> JsonDict: ...


class WeatherService:
    """Application service for Weather use cases."""

    def __init__(self, provider: WeatherProviderPort, provider_name: str = "openweather") -> None:
        """Create Weather service."""
        self._provider = provider
        self._provider_name = provider_name

    def current(self, city: str, country: str | None, units: str) -> dict[str, object]:
        """Return normalized current weather."""
        safe_units = validate_units(units)
        return self._call("current", city, lambda c: normalizer.current(self._provider.current(c, country, safe_units), safe_units))

    def forecast(self, city: str, days: int, units: str) -> dict[str, object]:
        """Return normalized daily forecast."""
        safe_days = forecast_days(days)
        safe_units = validate_units(units)
        return self._call("forecast", city, lambda c: normalizer.daily(self._provider.daily_forecast(c, safe_days, safe_units), safe_units))

    def hourly(self, city: str, units: str) -> dict[str, object]:
        """Return normalized hourly forecast."""
        return self._call("hourly", city, lambda c: normalizer.hourly(self._provider.hourly_forecast(c, validate_units(units))))

    def air_quality(self, city: str) -> dict[str, object]:
        """Return normalized air quality."""
        return self._call("air_quality", city, lambda c: normalizer.air_quality(self._provider.air_quality(c)))

    def uv(self, city: str, units: str) -> dict[str, object]:
        """Return normalized UV index."""
        safe_units = validate_units(units)
        return self._call("uv", city, lambda c: normalizer.uv(self._provider.current(c, None, safe_units)))

    def alerts(self, city: str, units: str) -> dict[str, object]:
        """Return normalized weather alerts."""
        safe_units = validate_units(units)
        return self._call("alerts", city, lambda c: normalizer.alerts(self._provider.current(c, None, safe_units)))

    def _call(self, endpoint: str, city: str, func: Callable[[str], dict[str, object]]) -> dict[str, object]:
        """Validate, execute, log, and return Weather data."""
        safe_city = validate_city(city)
        started = perf_counter()
        data = func(safe_city)
        coords = data.get("coordinates", {})
        if isinstance(coords, dict):
            coordinates(coords.get("latitude"), coords.get("longitude"))
        logger.info("weather_request", endpoint=endpoint, city=safe_city, latency=round((perf_counter() - started) * 1000, 2), provider=self._provider_name, status="ok")
        return data
