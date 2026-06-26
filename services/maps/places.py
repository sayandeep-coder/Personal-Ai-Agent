"""Place normalizers.

Purpose: normalize Google Places payloads.
Responsibilities: shape search, nearby, detail, and autocomplete responses.
Dependencies: Maps common helpers.
Extension Notes: add photo proxying instead of raw photo references later.
"""

from integrations.maps.transport import JsonDict
from services.maps.common import as_dict, as_list, location


def search(payload: JsonDict) -> dict[str, object]:
    """Return normalized place search results."""
    return {"places": [_place(item) for item in as_list(payload.get("results")) if isinstance(item, dict)]}


def nearby(payload: JsonDict) -> dict[str, object]:
    """Return normalized nearby results."""
    places = []
    for item in as_list(payload.get("results")):
        if isinstance(item, dict):
            value = _place(item)
            value["distance_meters"] = item.get("distance_meters", 0)
            places.append(value)
    return {"places": places}


def details(payload: JsonDict) -> dict[str, object]:
    """Return normalized place details."""
    item = as_dict(payload.get("result"))
    hours = as_dict(item.get("opening_hours"))
    return _place(item) | {
        "contact": {"phone_number": item.get("formatted_phone_number"), "website": item.get("website")},
        "opening_hours": {"open_now": hours.get("open_now"), "weekday_text": hours.get("weekday_text", [])},
        "reviews_count": item.get("user_ratings_total", 0),
        "photos": [_photo(photo) for photo in as_list(item.get("photos")) if isinstance(photo, dict)],
    }


def autocomplete(payload: JsonDict) -> dict[str, object]:
    """Return normalized autocomplete predictions."""
    return {"predictions": [_prediction(item) for item in as_list(payload.get("predictions")) if isinstance(item, dict)]}


def _place(item: JsonDict) -> dict[str, object]:
    return {
        "place_id": item.get("place_id", ""),
        "name": item.get("name", ""),
        "formatted_address": item.get("formatted_address") or item.get("vicinity", ""),
        "location": location(item),
        "rating": item.get("rating"),
        "total_ratings": item.get("user_ratings_total", 0),
        "business_status": item.get("business_status"),
        "open_now": as_dict(item.get("opening_hours")).get("open_now"),
        "price_level": item.get("price_level"),
        "types": as_list(item.get("types")),
    }


def _prediction(item: JsonDict) -> dict[str, object]:
    return {"place_id": item.get("place_id", ""), "description": item.get("description", ""), "matched_substrings": as_list(item.get("matched_substrings"))}


def _photo(photo: JsonDict) -> object:
    return photo.get("photo_reference")
