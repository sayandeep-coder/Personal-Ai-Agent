"""Gmail CLI commands."""

import typer

from apps.cli.google_factory import run_with_service
from apps.cli.console import console
from apps.cli.output import render_mapping
from apps.api.routes.google.factory import gmail

gmail_app = typer.Typer(help="Gmail commands.")


@gmail_app.command("list")
def list_messages(email: str, max_results: int = 10) -> None:
    """List Gmail messages."""
    run_with_service(gmail, lambda service: render_mapping(console, "Gmail", service.list_messages(email, max_results=max_results)))


@gmail_app.command("read")
def read(email: str, message_id: str) -> None:
    """Read Gmail message."""
    run_with_service(gmail, lambda service: render_mapping(console, "Message", service.get_message(email, message_id)))


@gmail_app.command("search")
def search(email: str, query: str) -> None:
    """Search Gmail messages."""
    run_with_service(gmail, lambda service: render_mapping(console, "Search", service.search_messages(email, query)))


@gmail_app.command("unread")
def unread(email: str) -> None:
    """Show unread count."""
    run_with_service(gmail, lambda service: render_mapping(console, "Unread", {"unread": service.unread_count(email)}))


@gmail_app.command("labels")
def labels(email: str) -> None:
    """Show Gmail labels."""
    run_with_service(gmail, lambda service: render_mapping(console, "Labels", service.labels(email)))


@gmail_app.command("send")
def send(email: str, recipient: str, subject: str, body: str) -> None:
    """Send Gmail message."""
    run_with_service(
        gmail,
        lambda service: render_mapping(console, "Sent", service.send_message(email, [recipient], subject, body)),
    )
