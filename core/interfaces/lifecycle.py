"""Lifecycle interfaces.

Purpose: define startup and shutdown contracts.
Responsibilities: support deterministic application bootstrap.
Dependencies: typing protocols.
Extension Notes: async lifecycle can be added beside this sync contract.
"""

from typing import Protocol


class Lifecycle(Protocol):
    """Protocol for services that own resources."""

    def start(self) -> None:
        """Initialize underlying resources."""
        ...

    def stop(self) -> None:
        """Release underlying resources."""
        ...

