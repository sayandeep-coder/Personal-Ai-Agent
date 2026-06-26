"""Calendar API routes.

Purpose: expose Google Calendar SDK wrapper endpoints.
Responsibilities: validate HTTP input and call CalendarService.
Dependencies: FastAPI and Google route factory.
Extension Notes: scheduling policy belongs above these routes.
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Query

from apps.api.dependencies import get_container
from apps.api.responses import success
from apps.api.routes.google import factory
from apps.api.schemas.google.calendar import CalendarEventWrite, CalendarWindow
from core.container import ServiceContainer

router = APIRouter(prefix="/calendar", tags=["calendar"])


def events(
    email: str = Query(...),
    window: CalendarWindow = Query(CalendarWindow.WEEK),
    calendar_id: str = Query("primary"),
    timezone: str = Query("Asia/Kolkata"),
    search: str | None = None,
    page_token: str | None = None,
    max_results: int = Query(10, ge=1, le=250),
    container: ServiceContainer = Depends(get_container),
) -> dict[str, object]:
    """Return normalized calendar events for a window."""
    start, end = _window(window, timezone)
    with container.database.get_session_factory()() as session:
        data = factory.calendar(container, session).events(
            email,
            start,
            end,
            max_results,
            calendar_id,
            page_token,
            search,
        )
    return success(data, {"window": window.value, "timezone": timezone})


def create_event(
    request: CalendarEventWrite,
    container: ServiceContainer = Depends(get_container),
) -> dict[str, object]:
    """Create a Google Calendar event."""
    with container.database.get_session_factory()() as session:
        payload = {"calendar_id": request.calendar_id, **request.to_google()}
        data = factory.calendar(container, session).create_event(str(request.email), payload)
    return success(data)


def update_event(
    id: str,
    request: CalendarEventWrite,
    container: ServiceContainer = Depends(get_container),
) -> dict[str, object]:
    """Update a Google Calendar event."""
    with container.database.get_session_factory()() as session:
        payload = {"calendar_id": request.calendar_id, **request.to_google()}
        data = factory.calendar(container, session).update_event(str(request.email), id, payload)
    return success(data)


def delete_event(
    id: str,
    email: str = Query(...),
    calendar_id: str = Query("primary"),
    container: ServiceContainer = Depends(get_container),
) -> dict[str, object]:
    """Delete calendar event."""
    with container.database.get_session_factory()() as session:
        data = factory.calendar(container, session).delete_event(email, id, calendar_id)
    return success(data)


def _window(window: CalendarWindow, timezone: str) -> tuple[str, str]:
    """Return ISO start and end for a named window."""
    now = datetime.now(ZoneInfo(timezone))
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    days = {CalendarWindow.TODAY: 1, CalendarWindow.WEEK: 7, CalendarWindow.MONTH: 31}
    return start.isoformat(), (start + timedelta(days=days[window])).isoformat()


router.add_api_route("/events", events, methods=["GET"])
router.add_api_route("/events", create_event, methods=["POST"])
router.add_api_route("/events/{id}", update_event, methods=["PATCH"])
router.add_api_route("/events/{id}", delete_event, methods=["DELETE"])
