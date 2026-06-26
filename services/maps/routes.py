"""Route and distance normalizers.

Purpose: normalize directions and distance matrix payloads.
Responsibilities: shape route, step, and matrix data.
Dependencies: Maps common helpers.
Extension Notes: add alternative routes when callers need them.
"""

from integrations.maps.transport import JsonDict
from services.maps.common import as_dict, as_list
from services.maps.formatting import distance, duration


def directions(payload: JsonDict) -> dict[str, object]:
    """Return normalized directions result."""
    route = _first(payload.get("routes"))
    leg = _first(route.get("legs"))
    return {"route": {
        "start_address": leg.get("start_address", ""),
        "end_address": leg.get("end_address", ""),
        "distance": distance(leg.get("distance")),
        "duration": duration(leg.get("duration")),
        "traffic_duration": duration(leg.get("duration_in_traffic")),
        "polyline": as_dict(route.get("overview_polyline")).get("points", ""),
        "steps": [_step(step) for step in as_list(leg.get("steps")) if isinstance(step, dict)],
    }}


def distance_matrix(payload: JsonDict) -> dict[str, object]:
    """Return normalized distance matrix."""
    origins = as_list(payload.get("origin_addresses"))
    destinations = as_list(payload.get("destination_addresses"))
    matrix = []
    for row_index, row in enumerate(as_list(payload.get("rows"))):
        elements = as_list(as_dict(row).get("elements"))
        for col_index, element in enumerate(elements):
            if isinstance(element, dict):
                matrix.append(_matrix_item(origins, destinations, row_index, col_index, element))
    return {"matrix": matrix}


def timezone(payload: JsonDict) -> dict[str, object]:
    """Return normalized timezone result."""
    raw = payload.get("rawOffset", 0)
    dst = payload.get("dstOffset", 0)
    raw_offset = int(raw) if isinstance(raw, int | str) else 0
    dst_offset = int(dst) if isinstance(dst, int | str) else 0
    return {
        "timezone_id": payload.get("timeZoneId", ""),
        "timezone_name": payload.get("timeZoneName", ""),
        "utc_offset_seconds": raw_offset + dst_offset,
    }


def _step(step: JsonDict) -> dict[str, object]:
    return {"instruction": step.get("html_instructions", ""), "distance": distance(step.get("distance")), "duration": duration(step.get("duration"))}


def _matrix_item(origins: list[object], destinations: list[object], row: int, col: int, item: JsonDict) -> dict[str, object]:
    return {
        "origin": origins[row] if row < len(origins) else "",
        "destination": destinations[col] if col < len(destinations) else "",
        "distance": distance(item.get("distance")),
        "duration": duration(item.get("duration")),
        "traffic_duration": duration(item.get("duration_in_traffic")),
        "travel_mode": item.get("travel_mode", "driving"),
        "status": item.get("status", "OK"),
    }


def _first(value: object) -> JsonDict:
    items = as_list(value)
    return as_dict(items[0]) if items and isinstance(items[0], dict) else {}
