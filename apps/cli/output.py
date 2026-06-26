"""CLI output helpers.

Purpose: render infrastructure data for humans.
Responsibilities: keep Rich presentation separate from command behavior.
Dependencies: Rich and health payloads.
Extension Notes: add JSON output mode without changing health checks.
"""

from collections.abc import Mapping, Sequence
from typing import Protocol

from rich.console import Console
from rich.table import Table


class DoctorCheckView(Protocol):
    """Protocol for rendering doctor check rows."""

    @property
    def name(self) -> str:
        """Return the check name."""
        ...

    @property
    def healthy(self) -> bool:
        """Return whether the check passed."""
        ...

    @property
    def detail(self) -> str:
        """Return the check detail."""
        ...


def render_help(console: Console) -> None:
    """Render top-level CLI help."""
    console.print("Usage: pa [OPTIONS] COMMAND [ARGS]...")
    console.print("")
    console.print("Personal AI Agent infrastructure CLI.")
    console.print("")
    console.print("Commands:")
    console.print("  version   Show application version metadata.")
    console.print("  health    Check configuration, database, and Redis health.")
    console.print("  config    Show non-sensitive configuration.")
    console.print("  doctor    Run infrastructure diagnostics.")
    console.print("  auth      Google authentication commands.")
    console.print("  gmail     Gmail commands.")
    console.print("  calendar  Calendar commands.")
    console.print("  drive     Drive commands.")
    console.print("  docs      Docs commands.")
    console.print("  sheets    Sheets commands.")
    console.print("  weather   Weather commands.")
    console.print("  maps      Google Maps commands.")


def render_health(console: Console, report: dict[str, object]) -> None:
    """Render an aggregate health report as a table."""
    table = Table(title=f"{report['application']} Health")
    table.add_column("Component")
    table.add_column("Healthy")
    table.add_column("Detail")
    checks = report.get("checks", {})
    if isinstance(checks, dict):
        for name, value in checks.items():
            if isinstance(value, dict):
                healthy = "yes" if value.get("healthy") else "no"
                table.add_row(str(name), healthy, str(value.get("detail", "")))
    console.print(table)


def render_mapping(console: Console, title: str, values: Mapping[str, object]) -> None:
    """Render key-value data as a Rich table."""
    table = Table(title=title)
    table.add_column("Key")
    table.add_column("Value")
    for key, value in values.items():
        table.add_row(key, str(value))
    console.print(table)


def render_doctor(console: Console, checks: Sequence[DoctorCheckView]) -> None:
    """Render doctor diagnostics as a Rich table."""
    table = Table(title="Doctor")
    table.add_column("Check")
    table.add_column("Healthy")
    table.add_column("Detail")
    for check in checks:
        healthy = "yes" if check.healthy else "no"
        table.add_row(check.name, healthy, check.detail)
    console.print(table)
