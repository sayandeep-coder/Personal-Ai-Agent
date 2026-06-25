"""Typer CLI bootstrap.

Purpose: provide local operational commands.
Responsibilities: initialize infrastructure and expose health checks.
Dependencies: Typer, Rich, settings, logging, and service container.
Extension Notes: split commands into modules when command surface grows.
"""

import sys

import typer
from rich.console import Console

from apps.cli.output import render_doctor, render_health, render_help, render_mapping

app = typer.Typer(
    name="pa",
    help="Personal AI Agent infrastructure CLI.",
    add_completion=False,
    rich_markup_mode=None,
    pretty_exceptions_enable=False,
)
console = Console()


@app.command()
def health() -> None:
    """Check configuration, database, and Redis health."""
    from core.constants import HEALTH_OK
    from core.factory import create_container
    from core.logging import configure_logging

    container = create_container()
    configure_logging(container.settings)
    container.start()
    try:
        report = container.health.check()
        render_health(console, report)
        if report.get("status") != HEALTH_OK:
            raise typer.Exit(code=1)
    finally:
        container.stop()


@app.command()
def version() -> None:
    """Show application version metadata."""
    from core.config import settings
    from core.metadata import ApplicationMetadata

    metadata = ApplicationMetadata(settings=settings)
    render_mapping(console, "Version", metadata.as_dict())


@app.command()
def config() -> None:
    """Show non-sensitive configuration."""
    from core.config import settings

    render_mapping(console, "Configuration", settings.safe_dict())


@app.command()
def doctor() -> None:
    """Run infrastructure diagnostics."""
    from apps.cli.doctor import run_doctor
    from core.factory import create_container
    from core.logging import configure_logging

    container = create_container()
    configure_logging(container.settings)
    container.start()
    try:
        checks = run_doctor(container)
        render_doctor(console, checks)
        if not all(check.healthy for check in checks):
            raise typer.Exit(code=1)
    finally:
        container.stop()


def main() -> None:
    """Console script entrypoint."""
    if any(arg in {"--help", "-h"} for arg in sys.argv[1:]):
        render_help(console)
        return
    app()


if __name__ == "__main__":
    main()
