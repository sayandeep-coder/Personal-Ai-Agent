"""Sheets CLI commands."""

import typer

from apps.api.routes.google.factory import sheets
from apps.cli.console import console
from apps.cli.google_factory import run_with_service
from apps.cli.output import render_mapping

sheets_app = typer.Typer(help="Sheets commands.")


@sheets_app.command("list")
def list_sheets(email: str) -> None:
    """List available spreadsheets."""
    run_with_service(sheets, lambda service: render_mapping(console, "Sheets", service.list_spreadsheets(email)))


@sheets_app.command("read")
def read(email: str, spreadsheet_id: str) -> None:
    """Read spreadsheet."""
    run_with_service(sheets, lambda service: render_mapping(console, "Sheet", service.read_spreadsheet(email, spreadsheet_id)))


@sheets_app.command("append")
def append(email: str, spreadsheet_id: str, cell_range: str, value: str) -> None:
    """Append row."""
    values: list[list[object]] = [[value]]
    run_with_service(sheets, lambda service: render_mapping(console, "Append", service.append_rows(email, spreadsheet_id, cell_range, values)))


@sheets_app.command("update")
def update(email: str, spreadsheet_id: str, cell_range: str, value: str) -> None:
    """Update cells."""
    values: list[list[object]] = [[value]]
    run_with_service(sheets, lambda service: render_mapping(console, "Update", service.update_cells(email, spreadsheet_id, cell_range, values)))
