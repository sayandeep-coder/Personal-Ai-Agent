"""Maps human-readable formatting helpers.

Purpose: format distances and durations for UI-ready Maps responses.
Responsibilities: preserve raw numeric values and provider display text.
Dependencies: standard math only.
Extension Notes: add locale-aware units when user preferences are available.
"""

from services.maps.common import as_dict


def distance(value: object) -> dict[str, object]:
    """Return normalized distance object."""
    item = as_dict(value)
    meters = _number(item.get("value"))
    return {
        "meters": meters,
        "kilometers": round(meters / 1000, 2) if meters is not None else None,
        "text": item.get("text") or _distance_text(meters),
    }


def duration(value: object) -> dict[str, object]:
    """Return normalized duration object."""
    item = as_dict(value)
    seconds = _number(item.get("value"))
    return {
        "seconds": seconds,
        "minutes": round(seconds / 60) if seconds is not None else None,
        "text": item.get("text") or _duration_text(seconds),
    }


def _number(value: object) -> int | None:
    """Return an integer number when possible."""
    return int(value) if isinstance(value, int | float | str) else None


def _distance_text(meters: int | None) -> str | None:
    """Return fallback distance text."""
    return f"{round(meters / 1000)} km" if meters is not None else None


def _duration_text(seconds: int | None) -> str | None:
    """Return fallback duration text."""
    return f"{round(seconds / 60)} mins" if seconds is not None else None
