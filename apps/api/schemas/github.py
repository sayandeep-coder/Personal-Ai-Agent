"""GitHub API query parameter schemas.

Purpose: validate and document all GitHub endpoint query parameters.
Responsibilities: constrain page sizes, enumerate valid sort/state values.
Dependencies: Pydantic v2.
Extension Notes: keep these thin — business logic belongs in the service layer.
"""

from enum import StrEnum

from pydantic import BaseModel, Field


class RepoSortOrder(StrEnum):
    """Allowed sort fields for repository listings."""

    STARS = "stars"
    UPDATED = "updated"
    CREATED = "created"
    PUSHED = "pushed"
    FULL_NAME = "full_name"


class IssueState(StrEnum):
    """Allowed issue/PR state filters."""

    OPEN = "open"
    CLOSED = "closed"
    ALL = "all"


class SearchSort(StrEnum):
    """Allowed sort fields for search results."""

    STARS = "stars"
    FORKS = "forks"
    UPDATED = "updated"
    BEST_MATCH = "best-match"


class PaginationParams(BaseModel):
    """Reusable pagination parameters."""

    page: int = Field(1, ge=1, le=100)
    per_page: int = Field(30, ge=1, le=100)
