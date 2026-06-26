"""Calendar response normalization.

Purpose: convert Calendar API objects into stable event contracts.
Responsibilities: map event fields, attendee emails, and pagination metadata.
Dependencies: Google Calendar JSON shapes.
Extension Notes: add recurrence summaries without exposing raw RRULE payloads.
"""

from integrations.google.common.http import JsonDict


def event(item: JsonDict) -> dict[str, object]:
    """Return a normalized calendar event."""
    return {
        "id": item.get("id", ""),
        "title": item.get("summary", ""),
        "description": item.get("description"),
        "location": item.get("location"),
        "start_time": _time(item.get("start")),
        "end_time": _time(item.get("end")),
        "timezone": _zone(item.get("start")),
        "attendees": _attendees(item),
        "html_link": item.get("htmlLink"),
        "status": item.get("status", ""),
    }


def event_page(payload: JsonDict) -> dict[str, object]:
    """Return a normalized page of events."""
    items = payload.get("items", [])
    items = items if isinstance(items, list) else []
    return {
        "events": [event(item) for item in items if isinstance(item, dict)],
        "next_page_token": payload.get("nextPageToken"),
    }


def _time(value: object) -> object:
    """Return event dateTime or all-day date."""
    return value.get("dateTime") or value.get("date") if isinstance(value, dict) else None


def _zone(value: object) -> object:
    """Return event timezone if present."""
    return value.get("timeZone") if isinstance(value, dict) else None


def _attendees(item: JsonDict) -> list[str]:
    """Return attendee email addresses."""
    raw = item.get("attendees", [])
    raw = raw if isinstance(raw, list) else []
    return [str(value.get("email")) for value in raw if isinstance(value, dict) and value.get("email")]
