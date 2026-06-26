"""Google Maps normalization helpers.

Purpose: share component and geometry extraction across Maps normalizers.
Responsibilities: map provider components into stable public fields.
Dependencies: Maps JSON alias.
Extension Notes: add localization support here if needed.
"""

from integrations.maps.transport import JsonDict


def location(item: JsonDict) -> dict[str, object]:
    """Return normalized latitude and longitude."""
    geometry = as_dict(item.get("geometry"))
    loc = as_dict(geometry.get("location"))
    return {"latitude": loc.get("lat"), "longitude": loc.get("lng")}


def components(item: JsonDict) -> dict[str, object]:
    """Return normalized address components."""
    values: dict[str, object] = {"city": None, "state": None, "country": None, "postal_code": None}
    raw = item.get("address_components", [])
    for part in raw if isinstance(raw, list) else []:
        if isinstance(part, dict):
            _assign(values, part)
    return values


def as_dict(value: object) -> JsonDict:
    """Return value as dict when possible."""
    return dict(value) if isinstance(value, dict) else {}


def as_list(value: object) -> list[object]:
    """Return value as list when possible."""
    return list(value) if isinstance(value, list) else []


def first_result(payload: JsonDict) -> JsonDict:
    """Return first result object."""
    items = as_list(payload.get("results"))
    return as_dict(items[0]) if items and isinstance(items[0], dict) else {}


def pagination(payload: JsonDict, count: int) -> dict[str, object]:
    """Return normalized pagination metadata."""
    return {"next_page_token": payload.get("next_page_token"), "total_results": count}


def _assign(values: dict[str, object], part: JsonDict) -> None:
    types = as_list(part.get("types"))
    name = part.get("long_name")
    if "locality" in types:
        values["city"] = name
    if "administrative_area_level_1" in types:
        values["state"] = name
    if "country" in types:
        values["country"] = name
    if "postal_code" in types:
        values["postal_code"] = name
