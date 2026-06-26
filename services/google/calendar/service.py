"""Google Calendar service wrapper.

Purpose: provide Calendar API operations.
Responsibilities: today/upcoming/search events, CRUD, calendars, freebusy.
Dependencies: Google credentials and REST client protocol.
Extension Notes: conflict policy belongs above this SDK wrapper.
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from integrations.google.common.http import GoogleApiPort, JsonDict
from services.google.calendar.normalizer import event, event_page
from services.google.protocols import AccessTokenProvider

BASE = "https://www.googleapis.com/calendar/v3"


class CalendarService:
    """Service wrapper for Google Calendar APIs."""

    def __init__(self, credentials: AccessTokenProvider, client: GoogleApiPort) -> None:
        """Create a Calendar service."""
        self._credentials = credentials
        self._client = client

    def today_events(self, email: str, timezone: str) -> JsonDict:
        """Return today's events."""
        now = datetime.now(ZoneInfo(timezone))
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        return self.events(email, start.isoformat(), end.isoformat())

    def upcoming_events(self, email: str, max_results: int = 10) -> JsonDict:
        """Return upcoming events."""
        return self.events(email, datetime.utcnow().isoformat() + "Z", None, max_results)

    def events(
        self,
        email: str,
        time_min: str,
        time_max: str | None = None,
        max_results: int = 10,
        calendar_id: str = "primary",
        page_token: str | None = None,
        query: str | None = None,
    ) -> JsonDict:
        """Return normalized events in a time range."""
        params: JsonDict = {"timeMin": time_min, "singleEvents": True, "maxResults": max_results}
        if time_max:
            params["timeMax"] = time_max
        if page_token:
            params["pageToken"] = page_token
        if query:
            params["q"] = query
        payload = self._client.get(f"{BASE}/calendars/{calendar_id}/events", self._token(email), params)
        return event_page(payload)

    def search_events(self, email: str, query: str) -> JsonDict:
        """Search calendar events."""
        payload = self._client.get(f"{BASE}/calendars/primary/events", self._token(email), {"q": query})
        return event_page(payload)

    def create_event(self, email: str, payload: JsonDict) -> JsonDict:
        """Create a calendar event."""
        calendar_id = str(payload.pop("calendar_id", "primary"))
        result = self._client.post(f"{BASE}/calendars/{calendar_id}/events", self._token(email), payload)
        return event(result)

    def update_event(self, email: str, event_id: str, payload: JsonDict) -> JsonDict:
        """Update a calendar event."""
        calendar_id = str(payload.pop("calendar_id", "primary"))
        result = self._client.patch(
            f"{BASE}/calendars/{calendar_id}/events/{event_id}",
            self._token(email),
            payload,
        )
        return event(result)

    def delete_event(self, email: str, event_id: str, calendar_id: str = "primary") -> JsonDict:
        """Delete a calendar event."""
        self._client.delete(f"{BASE}/calendars/{calendar_id}/events/{event_id}", self._token(email))
        return {"deleted": True, "id": event_id}

    def calendars(self, email: str) -> JsonDict:
        """Return calendar list."""
        return self._client.get(f"{BASE}/users/me/calendarList", self._token(email))

    def freebusy(self, email: str, payload: JsonDict) -> JsonDict:
        """Return freebusy data."""
        return self._client.post(f"{BASE}/freeBusy", self._token(email), payload)

    def _token(self, email: str) -> str:
        """Return access token for user email."""
        return self._credentials.access_token(email)
