"""Google Maps provider adapter.

Purpose: encapsulate Google Maps API endpoint calls.
Responsibilities: attach API key and call Maps endpoints through transport.
Dependencies: settings, Maps transport, and Maps errors.
Extension Notes: add field masks or alternate providers here later.
"""

from pydantic import SecretStr

from core.config import Settings
from integrations.maps.errors import maps_error
from integrations.maps.transport import JsonDict, MapsTransport


class GoogleMapsProvider:
    """Google Maps API provider."""

    def __init__(self, settings: Settings, transport: MapsTransport) -> None:
        """Create provider."""
        self._api_key = _api_key(settings.google_maps_api_key)
        self._transport = transport

    def geocode(self, address: str) -> JsonDict:
        """Return geocoding payload."""
        return self._get("/maps/api/geocode/json", {"address": address})

    def reverse_geocode(self, latitude: float, longitude: float) -> JsonDict:
        """Return reverse geocoding payload."""
        return self._get("/maps/api/geocode/json", {"latlng": f"{latitude},{longitude}"})

    def place_search(self, query: str, page_token: str | None = None) -> JsonDict:
        """Return text search payload."""
        return self._get("/maps/api/place/textsearch/json", {"query": query, "pagetoken": page_token})

    def nearby(self, latitude: float, longitude: float, radius: int, keyword: str | None) -> JsonDict:
        """Return nearby search payload."""
        return self._get("/maps/api/place/nearbysearch/json", {"location": f"{latitude},{longitude}", "radius": radius, "keyword": keyword})

    def details(self, place_id: str) -> JsonDict:
        """Return place details payload."""
        fields = "place_id,name,formatted_address,geometry,rating,user_ratings_total,business_status,price_level,types,formatted_phone_number,website,opening_hours,photos"
        return self._get("/maps/api/place/details/json", {"place_id": place_id, "fields": fields})

    def autocomplete(self, text: str) -> JsonDict:
        """Return autocomplete payload."""
        return self._get("/maps/api/place/autocomplete/json", {"input": text})

    def directions(self, origin: str, destination: str, mode: str) -> JsonDict:
        """Return directions payload."""
        return self._get("/maps/api/directions/json", {"origin": origin, "destination": destination, "mode": mode, "departure_time": "now"})

    def distance_matrix(self, origins: str, destinations: str, mode: str) -> JsonDict:
        """Return distance matrix payload."""
        return self._get("/maps/api/distancematrix/json", {"origins": origins, "destinations": destinations, "mode": mode, "departure_time": "now"})

    def timezone(self, latitude: float, longitude: float, timestamp: int) -> JsonDict:
        """Return timezone payload."""
        return self._get("/maps/api/timezone/json", {"location": f"{latitude},{longitude}", "timestamp": timestamp})

    def _get(self, path: str, params: dict[str, object]) -> JsonDict:
        """Execute a provider request with API key."""
        return self._transport.get(path, params | {"key": self._api_key})


def _api_key(value: SecretStr | None) -> str:
    """Return configured Google Maps API key."""
    if value is None:
        raise maps_error("unauthorized", "Google Maps API key is not configured.", 401)
    return value.get_secret_value()
