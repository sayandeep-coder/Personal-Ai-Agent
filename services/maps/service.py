"""Google Maps service.

Purpose: provide normalized Maps use cases to API and CLI callers.
Responsibilities: validate inputs, call provider, normalize results, and log.
Dependencies: Maps provider, normalizers, validation, and logging.
Extension Notes: add caching at this layer when rate limiting requires it.
"""

from collections.abc import Callable
from time import perf_counter
from typing import Protocol

from integrations.maps.transport import JsonDict
from core.logging import get_logger
from services.maps import geocode as geo, places, routes
from services.maps.common import as_list, pagination
from services.maps.types import MapsResult
from services.maps.validation import coordinate, mode as valid_mode, radius as valid_radius, text

logger = get_logger(__name__)


class MapsProviderPort(Protocol):
    def geocode(self, address: str) -> JsonDict: ...
    def reverse_geocode(self, latitude: float, longitude: float) -> JsonDict: ...
    def place_search(self, query: str, page_token: str | None = None) -> JsonDict: ...
    def nearby(self, latitude: float, longitude: float, radius: int, keyword: str | None) -> JsonDict: ...
    def details(self, place_id: str) -> JsonDict: ...
    def autocomplete(self, text: str) -> JsonDict: ...
    def directions(self, origin: str, destination: str, mode: str) -> JsonDict: ...
    def distance_matrix(self, origins: str, destinations: str, mode: str) -> JsonDict: ...
    def timezone(self, latitude: float, longitude: float, timestamp: int) -> JsonDict: ...


class MapsService:
    """Application service for Google Maps operations."""

    def __init__(self, provider: MapsProviderPort) -> None:
        self._provider = provider

    def geocode(self, address: str) -> MapsResult:
        return self._call("geocode", lambda: MapsResult(geo.geocode(self._provider.geocode(text(address, "address")))))

    def reverse_geocode(self, latitude: float, longitude: float) -> MapsResult:
        lat, lon = coordinate(latitude, longitude)
        return self._call("reverse_geocode", lambda: MapsResult(geo.reverse_geocode(self._provider.reverse_geocode(lat, lon))))

    def place_search(self, query: str, page_token: str | None) -> MapsResult:
        payload = self._provider.place_search(text(query, "query"), page_token)
        return self._page("place_search", places.search(payload), payload)

    def nearby(self, latitude: float, longitude: float, radius: int, keyword: str | None) -> MapsResult:
        lat, lon = coordinate(latitude, longitude)
        payload = self._provider.nearby(lat, lon, valid_radius(radius), keyword)
        return self._page("nearby", places.nearby(payload), payload)

    def details(self, place_id: str) -> MapsResult:
        return self._call("details", lambda: MapsResult(places.details(self._provider.details(text(place_id, "place_id")))))

    def autocomplete(self, value: str) -> MapsResult:
        payload = self._provider.autocomplete(text(value, "input"))
        return self._page("autocomplete", places.autocomplete(payload), payload, "predictions")

    def directions(self, origin: str, destination: str, mode: str) -> MapsResult:
        payload = self._provider.directions(text(origin, "origin"), text(destination, "destination"), valid_mode(mode))
        return self._call("directions", lambda: MapsResult(routes.directions(payload)))

    def distance_matrix(self, origins: str, destinations: str, mode: str) -> MapsResult:
        payload = self._provider.distance_matrix(text(origins, "origins"), text(destinations, "destinations"), valid_mode(mode))
        return self._call("distance_matrix", lambda: MapsResult(routes.distance_matrix(payload)))

    def timezone(self, latitude: float, longitude: float, timestamp: int) -> MapsResult:
        lat, lon = coordinate(latitude, longitude)
        return self._call("timezone", lambda: MapsResult(routes.timezone(self._provider.timezone(lat, lon, timestamp))))

    def _page(self, endpoint: str, data: dict[str, object], payload: JsonDict, key: str = "results") -> MapsResult:
        return self._call(endpoint, lambda: MapsResult(data, pagination(payload, len(as_list(payload.get(key))))))

    def _call(self, endpoint: str, func: Callable[[], MapsResult]) -> MapsResult:
        started = perf_counter()
        result = func()
        logger.info("maps_request", endpoint=endpoint, latency=round((perf_counter() - started) * 1000, 2), provider="google_maps", status="ok")
        return result
