"""Geocoding normalizers.

Purpose: normalize geocoding and reverse geocoding payloads.
Responsibilities: expose stable address, place, coordinate, and component fields.
Dependencies: Maps common helpers.
Extension Notes: include multiple candidates if product requirements need it.
"""

from integrations.maps.transport import JsonDict
from services.maps.common import components, first_result, location


def geocode(payload: JsonDict) -> dict[str, object]:
    """Return normalized geocoding result."""
    item = first_result(payload)
    plus = payload.get("plus_code", {})
    return {
        "formatted_address": item.get("formatted_address", ""),
        "place_id": item.get("place_id", ""),
        "location": location(item),
        "components": components(item),
        "plus_code": plus.get("global_code") if isinstance(plus, dict) else None,
    }


def reverse_geocode(payload: JsonDict) -> dict[str, object]:
    """Return normalized reverse geocoding result."""
    item = first_result(payload)
    return {
        "formatted_address": item.get("formatted_address", ""),
        "place_id": item.get("place_id", ""),
        "components": components(item),
    }
