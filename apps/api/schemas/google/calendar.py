"""Calendar API schemas.

Purpose: validate Calendar requests and document event contracts.
Responsibilities: define event create/update/list shapes.
Dependencies: Pydantic v2.
Extension Notes: add recurrence and resource booking schemas later.
"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, EmailStr, Field


class CalendarWindow(StrEnum):
    """Supported event list windows."""

    TODAY = "today"
    WEEK = "week"
    MONTH = "month"


class CalendarEventWrite(BaseModel):
    """Complete event creation or update payload."""

    email: EmailStr = Field(..., examples=["user@example.com"])
    calendar_id: str = Field("primary", examples=["primary"])
    title: str | None = Field(None, examples=["Project Meeting"])
    description: str | None = Field(None, examples=["Discuss AI Agent"])
    location: str | None = Field(None, examples=["Google Meet"])
    start_time: datetime | None = Field(None, examples=["2026-06-30T10:00:00+05:30"])
    end_time: datetime | None = Field(None, examples=["2026-06-30T11:00:00+05:30"])
    timezone: str = Field("Asia/Kolkata", examples=["Asia/Kolkata"])
    attendees: list[EmailStr] = Field(default_factory=list)
    conference: bool = False
    color: str | None = Field(None, examples=["5"])
    visibility: str = Field("default", examples=["default"])
    reminders: list[int] = Field(default_factory=list, examples=[[10, 30]])

    def to_google(self) -> dict[str, object]:
        """Return a Google Calendar event body."""
        body: dict[str, object] = {
            "summary": self.title,
            "description": self.description,
            "location": self.location,
            "visibility": self.visibility,
        }
        if self.start_time:
            body["start"] = {"dateTime": self.start_time.isoformat(), "timeZone": self.timezone}
        if self.end_time:
            body["end"] = {"dateTime": self.end_time.isoformat(), "timeZone": self.timezone}
        if self.attendees:
            body["attendees"] = [{"email": str(email)} for email in self.attendees]
        if self.color:
            body["colorId"] = self.color
        if self.reminders:
            body["reminders"] = {"useDefault": False, "overrides": _reminders(self.reminders)}
        if self.conference:
            body["conferenceData"] = {"createRequest": {"requestId": "personal-ai-agent"}}
        return {key: value for key, value in body.items() if value is not None}


def _reminders(minutes: list[int]) -> list[dict[str, object]]:
    """Return Google reminder overrides."""
    return [{"method": "popup", "minutes": minute} for minute in minutes]
