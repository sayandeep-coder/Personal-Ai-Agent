"""Google Maps input validation.

Purpose: reject invalid Maps inputs before provider calls.
Responsibilities: validate text, coordinates, radius, and travel mode.
Dependencies: Maps errors.
Extension Notes: add place type validation when endpoints expose type filters.
"""

from integrations.maps.errors import maps_error

VALID_MODES = frozenset({"driving", "walking", "bicycling", "transit"})


def text(value: str, field: str) -> str:
    """Validate non-empty text fields."""
    normalized = value.strip()
    if not normalized or len(normalized) > 500:
        raise maps_error("invalid_request", f"{field} must be a non-empty value.", 400)
    return normalized


def coordinate(latitude: float, longitude: float) -> tuple[float, float]:
    """Validate latitude and longitude."""
    if latitude < -90 or latitude > 90 or longitude < -180 or longitude > 180:
        raise maps_error("invalid_request", "Coordinates are out of range.", 400)
    return latitude, longitude


def radius(value: int) -> int:
    """Validate nearby search radius."""
    if value < 1 or value > 50000:
        raise maps_error("invalid_request", "Radius must be between 1 and 50000 meters.", 400)
    return value


def mode(value: str) -> str:
    """Validate travel mode."""
    if value not in VALID_MODES:
        raise maps_error("invalid_request", "Mode must be driving, walking, bicycling, or transit.", 400)
    return value
