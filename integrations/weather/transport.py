"""Weather provider transport.

Purpose: execute Weather API HTTP requests with timeout and retry.
Responsibilities: encode params, parse JSON, map provider failures safely.
Dependencies: urllib, standard JSON, and weather exceptions.
Extension Notes: replace urllib with async transport behind this protocol later.
"""

from collections.abc import Mapping
from time import sleep
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json
import socket
import ssl

from integrations.weather.errors import weather_error
from integrations.weather.ssl import weather_ssl_context

JsonDict = dict[str, object]
JsonPayload = JsonDict | list[object]


class WeatherTransport(Protocol):
    """Protocol for Weather provider HTTP transport."""

    def get(self, path: str, params: Mapping[str, object]) -> JsonPayload:
        """Execute a Weather API GET request."""
        ...


class UrllibWeatherTransport:
    """urllib Weather transport with timeout and exponential retry."""

    def __init__(self, base_url: str = "https://api.openweathermap.org", timeout: int = 10) -> None:
        """Create a Weather transport."""
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._ssl_context = weather_ssl_context()

    def get(self, path: str, params: Mapping[str, object]) -> JsonPayload:
        """Execute a retried GET request."""
        query = urlencode({key: value for key, value in params.items() if value is not None})
        request = Request(f"{self._base_url}{path}?{query}", method="GET")
        for attempt in range(3):
            try:
                with urlopen(request, timeout=self._timeout, context=self._ssl_context) as response:
                    data = json.loads(response.read().decode())
                    return data if isinstance(data, list) else dict(data)
            except HTTPError as exc:
                if exc.code not in {429, 500, 503} or attempt == 2:
                    raise _http_error(exc) from exc
                sleep(0.2 * (2**attempt))
            except (TimeoutError, socket.timeout) as exc:
                raise weather_error("timeout", "Weather provider timed out.", 503) from exc
            except URLError as exc:
                if isinstance(exc.reason, ssl.SSLError):
                    raise weather_error("unavailable", "Weather provider TLS verification failed.", 503) from exc
                if attempt == 2:
                    raise weather_error("unavailable", "Weather provider is unavailable.", 503) from exc
                sleep(0.2 * (2**attempt))
        raise weather_error("unavailable", "Weather provider is unavailable.", 503)


def _http_error(exc: HTTPError) -> Exception:
    """Map provider HTTP errors to safe application exceptions."""
    mapping = {
        401: ("invalid_key", "Weather API key is invalid.", 401),
        404: ("not_found", "Weather location was not found.", 404),
        429: ("rate_limited", "Weather provider rate limit exceeded.", 429),
        500: ("provider_error", "Weather provider failed.", 500),
        503: ("unavailable", "Weather provider is unavailable.", 503),
    }
    code, message, status = mapping.get(exc.code, ("provider_error", "Weather provider request failed.", 500))
    return weather_error(code, message, status)
