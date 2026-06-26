"""Maps service types.

Purpose: define reusable result objects for Maps operations.
Responsibilities: carry data and pagination metadata separately.
Dependencies: dataclasses.
Extension Notes: add cache metadata when Maps caching is introduced.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class MapsResult:
    """Normalized Maps service result."""

    data: dict[str, object]
    pagination: dict[str, object] = field(default_factory=lambda: {"next_page_token": None, "total_results": 0})
