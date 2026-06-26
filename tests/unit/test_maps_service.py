"""Google Maps service tests.

Purpose: verify Maps service normalization and validation.
Responsibilities: cover every Maps use case without network calls.
Dependencies: pytest, MapsService, and fakes.
Extension Notes: add live provider contract tests only with sandbox keys.
"""

import pytest

from core.exceptions import ValidationException
from services.maps.service import MapsService
from tests.unit.maps_fakes import MapsProvider


def test_geocode_and_reverse_geocode() -> None:
    service = MapsService(MapsProvider())
    assert service.geocode("Kolkata").data["place_id"] == "p1"
    components = service.reverse_geocode(22.57, 88.36).data["components"]
    assert isinstance(components, dict)
    assert components["country"] == "India"


def test_places_search_nearby_details_autocomplete() -> None:
    service = MapsService(MapsProvider())
    assert service.place_search("coffee", None).pagination["next_page_token"] == "next"
    assert service.nearby(22.57, 88.36, 1000, "coffee").data["places"]
    contact = service.details("p1").data["contact"]
    assert isinstance(contact, dict)
    assert contact["website"] == "https://example.com"
    assert service.autocomplete("kol").data["predictions"]


def test_directions_distance_matrix_timezone() -> None:
    service = MapsService(MapsProvider())
    route = service.directions("A", "B", "driving").data["route"]
    assert isinstance(route, dict)
    assert route["distance"] == {"meters": 100, "kilometers": 0.1, "text": "100 m"}
    matrix = service.distance_matrix("A", "B", "driving").data["matrix"]
    assert isinstance(matrix, list)
    assert matrix[0]["distance"]["text"] == "10 km"
    assert matrix[0]["traffic_duration"]["minutes"] == 22
    assert matrix[0]["travel_mode"] == "driving"
    assert service.timezone(22.57, 88.36, 1).data["timezone_id"] == "Asia/Kolkata"


def test_invalid_inputs() -> None:
    service = MapsService(MapsProvider())
    with pytest.raises(ValidationException):
        service.geocode("")
    with pytest.raises(ValidationException):
        service.reverse_geocode(100, 88)
    with pytest.raises(ValidationException):
        service.directions("A", "B", "flying")
