"""GitHub API client protocol.

Purpose: define the interface for authorized GitHub REST API calls.
Responsibilities: decouple service layer from concrete HTTP implementation.
Dependencies: typing protocols.
Extension Notes: swap implementation for httpx or aiohttp without changing services.
"""

from typing import Protocol

JsonDict = dict[str, object]


class GitHubApiPort(Protocol):
    """Read-only, public-data GitHub REST API client."""

    def get(self, path: str, params: JsonDict | None = None) -> JsonDict:
        """Execute an authorized GET request and return parsed JSON."""
        ...

    def get_list(self, path: str, params: JsonDict | None = None) -> list[JsonDict]:
        """Execute an authorized GET request and return a parsed JSON list."""
        ...
