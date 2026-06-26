"""Google CLI service factory.

Purpose: create Google services for CLI commands.
Responsibilities: share container/session wiring across command groups.
Dependencies: infrastructure container and Google service factory.
Extension Notes: add output modes here if CLI formats expand.
"""

from collections.abc import Callable
from typing import TypeVar

from core.container import ServiceContainer
from core.factory import create_container
from sqlalchemy.orm import Session

ServiceT = TypeVar("ServiceT")


def run_with_service(
    factory: Callable[[ServiceContainer, Session], ServiceT],
    action: Callable[[ServiceT], None],
) -> None:
    """Run a CLI action with a Google service instance."""
    container = create_container()
    container.start()
    try:
        with container.database.get_session_factory()() as session:
            action(factory(container, session))
    finally:
        container.stop()
