"""Google Maps API schemas.

Purpose: define reusable query validation enums for Maps routes.
Responsibilities: expose typed travel modes to OpenAPI.
Dependencies: Python enums.
Extension Notes: add place type enums when search filters expand.
"""

from enum import StrEnum


class TravelMode(StrEnum):
    """Supported Google Maps travel modes."""

    DRIVING = "driving"
    WALKING = "walking"
    BICYCLING = "bicycling"
    TRANSIT = "transit"
