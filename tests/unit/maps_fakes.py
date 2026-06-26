"""Google Maps test fakes.

Purpose: provide deterministic provider payloads for Maps service tests.
Responsibilities: simulate all supported Maps endpoints.
Dependencies: Maps JSON alias.
Extension Notes: add provider failure fakes as policies grow.
"""

from integrations.maps.transport import JsonDict


class MapsProvider:
    """Fake Maps provider."""

    def geocode(self, address: str) -> JsonDict:
        return {"results": [_place(address)]}

    def reverse_geocode(self, latitude: float, longitude: float) -> JsonDict:
        return {"results": [_place("Kolkata")]}

    def place_search(self, query: str, page_token: str | None = None) -> JsonDict:
        return {"results": [_place(query)], "next_page_token": "next"}

    def nearby(self, latitude: float, longitude: float, radius: int, keyword: str | None) -> JsonDict:
        return {"results": [_place(keyword or "Cafe")]}

    def details(self, place_id: str) -> JsonDict:
        return {"result": _place("Cafe") | {"formatted_phone_number": "123", "website": "https://example.com"}}

    def autocomplete(self, text: str) -> JsonDict:
        return {"predictions": [{"place_id": "p1", "description": text, "matched_substrings": [{"offset": 0, "length": 3}]}]}

    def directions(self, origin: str, destination: str, mode: str) -> JsonDict:
        leg = {"start_address": origin, "end_address": destination, "distance": {"value": 100, "text": "100 m"}, "duration": {"value": 60, "text": "1 min"}, "steps": []}
        return {"routes": [{"legs": [leg], "overview_polyline": {"points": "abc"}}]}

    def distance_matrix(self, origins: str, destinations: str, mode: str) -> JsonDict:
        element = {"distance": {"value": 9954, "text": "10 km"}, "duration": {"value": 1361, "text": "23 mins"}, "duration_in_traffic": {"value": 1334, "text": "22 mins"}, "status": "OK", "travel_mode": mode}
        return {"origin_addresses": [origins], "destination_addresses": [destinations], "rows": [{"elements": [element]}]}

    def timezone(self, latitude: float, longitude: float, timestamp: int) -> JsonDict:
        return {"timeZoneId": "Asia/Kolkata", "timeZoneName": "India Standard Time", "rawOffset": 19800, "dstOffset": 0}


def _place(name: str) -> JsonDict:
    """Return a fake Maps place."""
    return {
        "place_id": "p1",
        "name": name,
        "formatted_address": "Kolkata, India",
        "geometry": {"location": {"lat": 22.57, "lng": 88.36}},
        "rating": 4.5,
        "user_ratings_total": 10,
        "business_status": "OPERATIONAL",
        "opening_hours": {"open_now": True, "weekday_text": ["Mon: Open"]},
        "price_level": 2,
        "types": ["restaurant"],
        "address_components": [{"long_name": "India", "types": ["country"]}],
    }
