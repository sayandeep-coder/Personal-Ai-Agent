"""Docs CLI commands."""

import typer

from apps.api.routes.google.factory import docs
from apps.cli.console import console
from apps.cli.google_factory import run_with_service
from apps.cli.output import render_mapping

docs_app = typer.Typer(help="Docs commands.")


@docs_app.command("list")
def list_docs(email: str) -> None:
    """List available documents."""
    run_with_service(docs, lambda service: render_mapping(console, "Documents", service.list_documents(email)))


@docs_app.command("create")
def create(email: str, title: str) -> None:
    """Create document."""
    run_with_service(docs, lambda service: render_mapping(console, "Document", service.create_document(email, title)))


@docs_app.command("read")
def read(email: str, document_id: str) -> None:
    """Read document."""
    run_with_service(docs, lambda service: render_mapping(console, "Document", service.read_document(email, document_id)))


@docs_app.command("append")
def append(email: str, document_id: str, text: str) -> None:
    """Append text."""
    run_with_service(docs, lambda service: render_mapping(console, "Append", service.append_text(email, document_id, text)))
