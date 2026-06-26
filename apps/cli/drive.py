"""Drive CLI commands."""

import typer

from apps.api.routes.google.factory import drive
from apps.cli.console import console
from apps.cli.google_factory import run_with_service
from apps.cli.output import render_mapping

drive_app = typer.Typer(help="Drive commands.")


@drive_app.command("list")
def list_files(email: str) -> None:
    """List Drive files."""
    run_with_service(drive, lambda service: render_mapping(console, "Files", service.list_files(email)))


@drive_app.command("upload")
def upload(email: str, name: str, content: str) -> None:
    """Upload a text file."""
    metadata: dict[str, object] = {"name": name, "mimeType": "text/plain"}
    run_with_service(drive, lambda service: render_mapping(console, "Upload", service.upload(email, metadata, content)))


@drive_app.command("download")
def download(email: str, file_id: str) -> None:
    """Download a file (prints metadata; binary content written to stdout)."""
    def _run(service: object) -> None:
        from services.google.drive.service import DriveService
        assert isinstance(service, DriveService)
        raw, content_type, filename = service.download(email, file_id)
        render_mapping(console, "Download", {"filename": filename, "content_type": content_type, "bytes": len(raw)})
    run_with_service(drive, _run)


@drive_app.command("delete")
def delete(email: str, file_id: str) -> None:
    """Delete a file."""
    run_with_service(drive, lambda service: render_mapping(console, "Delete", service.delete(email, file_id)))
