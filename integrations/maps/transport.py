"""Google Maps transport.

Purpose: execute Google Maps API requests with retry and timeout.
Responsibilities: encode params, parse JSON, and map failures safely.
Dependencies: urllib and Maps exceptions.
Extension Notes: replace with async transport without changing services.
"""

from collections.abc import Mapping
from time import sleep
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json
import socket

from integrations.maps.errors import maps_error
from integrations.maps.ssl import maps_ssl_context

JsonDict = dict[str, object]


class MapsTransport(Protocol):
    """Protocol for Maps provider transport."""

    def get(self, path: str, params: Mapping[str, object]) -> JsonDict:
        """Execute a Maps API GET request."""
        ...


class UrllibMapsTransport:
    """urllib-backed Google Maps transport."""

    def __init__(self, base_url: str = "https://maps.googleapis.com", timeout: int = 10) -> None:
        """Create transport."""
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._ssl_context = maps_ssl_context()

    def get(self, path: str, params: Mapping[str, object]) -> JsonDict:
        """Execute a retried GET request."""
        query = urlencode({key: value for key, value in params.items() if value is not None})
        request = Request(f"{self._base_url}{path}?{query}", method="GET")
        for attempt in range(3):
            try:
                with urlopen(request, timeout=self._timeout, context=self._ssl_context) as response:
                    return _checked(dict(json.loads(response.read().decode())))
            except HTTPError as exc:
                if exc.code not in {429, 500, 503} or attempt == 2:
                    raise _http_error(exc.code) from exc
                sleep(0.2 * (2**attempt))
            except (TimeoutError, socket.timeout) as exc:
                raise maps_error("timeout", "Google Maps request timed out.", 503) from exc
            except URLError as exc:
                if attempt == 2:
                    raise maps_error("provider_error", "Google Maps provider is unavailable.", 503) from exc
                sleep(0.2 * (2**attempt))
        raise maps_error("provider_error", "Google Maps provider is unavailable.", 503)


def _checked(payload: JsonDict) -> JsonDict:
    """Validate Google Maps API status."""
    status = str(payload.get("status", "OK"))
    if status in {"OK", "ZERO_RESULTS"}:
        return payload
    code, http = _provider_status(status)
    message = str(payload.get("error_message") or f"Google Maps returned {status}.")
    raise maps_error(code, message, http)


def _provider_status(status: str) -> tuple[str, int]:
    mapping = {"REQUEST_DENIED": ("forbidden", 403), "INVALID_REQUEST": ("invalid_request", 400), "OVER_QUERY_LIMIT": ("rate_limited", 429), "NOT_FOUND": ("not_found", 404)}
    return mapping.get(status, ("provider_error", 500))


def _http_error(status: int) -> Exception:
    mapping = {400: ("invalid_request", 400), 401: ("unauthorized", 401), 403: ("forbidden", 403), 404: ("not_found", 404), 429: ("rate_limited", 429), 503: ("provider_error", 503)}
    code, http = mapping.get(status, ("provider_error", 500))
    return maps_error(code, "Google Maps request failed.", http)
