"""Base registry abstractions.

Purpose: provide a small extension point for named infrastructure objects.
Responsibilities: register and retrieve objects without global mutation.
Dependencies: dataclasses and generic typing.
Extension Notes: specialize this for tools or integrations in later phases.
"""

from dataclasses import dataclass, field
from typing import Generic, TypeVar

from core.exceptions import ValidationException

ItemT = TypeVar("ItemT")


@dataclass
class Registry(Generic[ItemT]):
    """In-memory registry owned by an injected service."""

    _items: dict[str, ItemT] = field(default_factory=dict)

    def register(self, name: str, item: ItemT) -> None:
        """Register an item under a unique name."""
        if name in self._items:
            raise ValidationException(
                message=f"Registry item already exists: {name}",
                code="registry.duplicate",
                details={"name": name},
            )
        self._items[name] = item

    def get(self, name: str) -> ItemT:
        """Return a registered item by name."""
        try:
            return self._items[name]
        except KeyError as exc:
            raise ValidationException(
                message=f"Registry item not found: {name}",
                code="registry.not_found",
                details={"name": name},
            ) from exc

    def names(self) -> tuple[str, ...]:
        """Return registered item names."""
        return tuple(self._items.keys())

