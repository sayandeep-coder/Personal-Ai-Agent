"""CLI console singleton.

Purpose: expose shared Rich console for command modules.
Responsibilities: avoid circular imports through apps.cli.main.
Dependencies: Rich.
Extension Notes: add console configuration here if output modes expand.
"""

from rich.console import Console

console = Console()

