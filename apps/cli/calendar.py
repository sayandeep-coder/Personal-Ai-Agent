"""Calendar CLI commands."""

import typer

from apps.api.routes.google.factory import calendar
from apps.cli.console import console
from apps.cli.google_factory import run_with_service
from apps.cli.output import render_mapping
from integrations.google.common.http import JsonDict

calendar_app = typer.Typer(help="Calendar commands.")


@calendar_app.command("today")
def today(email: str, timezone: str = "Asia/Kolkata") -> None:
    """Show today's events."""
    run_with_service(calendar, lambda service: render_mapping(console, "Today", service.today_events(email, timezone)))


@calendar_app.command("upcoming")
def upcoming(email: str) -> None:
    """Show upcoming events."""
    run_with_service(calendar, lambda service: render_mapping(console, "Upcoming", service.upcoming_events(email)))


@calendar_app.command("create")
def create(email: str, summary: str) -> None:
    """Create a simple event payload."""
    payload: JsonDict = {"summary": summary}
    run_with_service(calendar, lambda service: render_mapping(console, "Created", service.create_event(email, payload)))


@calendar_app.command("delete")
def delete(email: str, event_id: str) -> None:
    """Delete an event."""
    run_with_service(calendar, lambda service: render_mapping(console, "Deleted", service.delete_event(email, event_id)))
