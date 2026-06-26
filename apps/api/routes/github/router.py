"""GitHub API routes.

Purpose: expose read-only public GitHub data via REST endpoints.
Responsibilities: validate HTTP input, delegate to GitHubService, return enveloped responses.
Dependencies: FastAPI, factory, schemas, response helpers.

Security notes:
  - No write or mutation operations exist in this module.
  - Private-repository enforcement is done in the SERVICE LAYER, not here.
  - GITHUB_TOKEN is never read, logged, or returned in any handler.
"""

from fastapi import APIRouter, Depends, Query

from apps.api.dependencies import get_container
from apps.api.responses import success
from apps.api.routes.github import factory
from apps.api.schemas.github import IssueState, RepoSortOrder, SearchSort
from core.container import ServiceContainer

router = APIRouter(prefix="/github", tags=["github"])


# ── User endpoints ────────────────────────────────────────────────────────────

def get_user(
    username: str,
    container: ServiceContainer = Depends(get_container),
) -> dict[str, object]:
    """Return the public profile of a GitHub user."""
    data = factory.github(container).get_user(username)
    return success(data)


def get_user_repos(
    username: str,
    page: int = Query(1, ge=1, le=100),
    per_page: int = Query(30, ge=1, le=100),
    sort: RepoSortOrder = Query(RepoSortOrder.UPDATED),
    container: ServiceContainer = Depends(get_container),
) -> dict[str, object]:
    """Return public repositories for a GitHub user."""
    data = factory.github(container).get_user_repos(username, page, per_page, sort.value)
    return success(data, {"page": page, "per_page": per_page})


# ── Repository endpoints ──────────────────────────────────────────────────────

def get_repo(
    owner: str,
    repo: str,
    container: ServiceContainer = Depends(get_container),
) -> dict[str, object]:
    """Return metadata for a public repository."""
    data = factory.github(container).get_repo(owner, repo)
    return success(data)


def get_readme(
    owner: str,
    repo: str,
    container: ServiceContainer = Depends(get_container),
) -> dict[str, object]:
    """Return the decoded README for a public repository."""
    data = factory.github(container).get_readme(owner, repo)
    return success(data)


def get_languages(
    owner: str,
    repo: str,
    container: ServiceContainer = Depends(get_container),
) -> dict[str, object]:
    """Return language breakdown for a public repository."""
    data = factory.github(container).get_languages(owner, repo)
    return success(data)


def get_contributors(
    owner: str,
    repo: str,
    page: int = Query(1, ge=1, le=100),
    per_page: int = Query(30, ge=1, le=100),
    container: ServiceContainer = Depends(get_container),
) -> dict[str, object]:
    """Return contributors for a public repository."""
    data = factory.github(container).get_contributors(owner, repo, page, per_page)
    return success(data, {"page": page, "per_page": per_page})


def get_branches(
    owner: str,
    repo: str,
    page: int = Query(1, ge=1, le=100),
    per_page: int = Query(30, ge=1, le=100),
    container: ServiceContainer = Depends(get_container),
) -> dict[str, object]:
    """Return branches for a public repository."""
    data = factory.github(container).get_branches(owner, repo, page, per_page)
    return success(data, {"page": page, "per_page": per_page})


def get_commits(
    owner: str,
    repo: str,
    page: int = Query(1, ge=1, le=100),
    per_page: int = Query(30, ge=1, le=100),
    branch: str | None = Query(None, description="Branch or SHA to filter commits"),
    container: ServiceContainer = Depends(get_container),
) -> dict[str, object]:
    """Return commits for a public repository."""
    data = factory.github(container).get_commits(owner, repo, page, per_page, branch)
    return success(data, {"page": page, "per_page": per_page})


def get_releases(
    owner: str,
    repo: str,
    page: int = Query(1, ge=1, le=100),
    per_page: int = Query(30, ge=1, le=100),
    container: ServiceContainer = Depends(get_container),
) -> dict[str, object]:
    """Return releases for a public repository."""
    data = factory.github(container).get_releases(owner, repo, page, per_page)
    return success(data, {"page": page, "per_page": per_page})


def get_issues(
    owner: str,
    repo: str,
    state: IssueState = Query(IssueState.OPEN),
    labels: str | None = Query(None, description="Comma-separated label names"),
    page: int = Query(1, ge=1, le=100),
    per_page: int = Query(30, ge=1, le=100),
    container: ServiceContainer = Depends(get_container),
) -> dict[str, object]:
    """Return issues for a public repository."""
    data = factory.github(container).get_issues(owner, repo, state.value, labels, page, per_page)
    return success(data, {"page": page, "per_page": per_page, "state": state})


def get_pulls(
    owner: str,
    repo: str,
    state: IssueState = Query(IssueState.OPEN),
    page: int = Query(1, ge=1, le=100),
    per_page: int = Query(30, ge=1, le=100),
    container: ServiceContainer = Depends(get_container),
) -> dict[str, object]:
    """Return pull requests for a public repository."""
    data = factory.github(container).get_pulls(owner, repo, state.value, page, per_page)
    return success(data, {"page": page, "per_page": per_page, "state": state})


def get_pull(
    owner: str,
    repo: str,
    pull_number: int,
    container: ServiceContainer = Depends(get_container),
) -> dict[str, object]:
    """Return a single pull request for a public repository."""
    data = factory.github(container).get_pull(owner, repo, pull_number)
    return success(data)


# ── Search endpoints ──────────────────────────────────────────────────────────

def search_repositories(
    q: str = Query(..., min_length=1, description="GitHub repository search query"),
    sort: SearchSort = Query(SearchSort.STARS),
    page: int = Query(1, ge=1, le=100),
    per_page: int = Query(30, ge=1, le=100),
    container: ServiceContainer = Depends(get_container),
) -> dict[str, object]:
    """Search public GitHub repositories."""
    data = factory.github(container).search_repositories(q, page, per_page, sort.value)
    return success(data, {"query": q, "page": page, "per_page": per_page})


def search_users(
    q: str = Query(..., min_length=1, description="GitHub user search query"),
    page: int = Query(1, ge=1, le=100),
    per_page: int = Query(30, ge=1, le=100),
    container: ServiceContainer = Depends(get_container),
) -> dict[str, object]:
    """Search GitHub users."""
    data = factory.github(container).search_users(q, page, per_page)
    return success(data, {"query": q, "page": page, "per_page": per_page})


# ── Route registration ────────────────────────────────────────────────────────

router.add_api_route("/users/{username}", get_user, methods=["GET"])
router.add_api_route("/users/{username}/repos", get_user_repos, methods=["GET"])

router.add_api_route("/repos/{owner}/{repo}", get_repo, methods=["GET"])
router.add_api_route("/repos/{owner}/{repo}/readme", get_readme, methods=["GET"])
router.add_api_route("/repos/{owner}/{repo}/languages", get_languages, methods=["GET"])
router.add_api_route("/repos/{owner}/{repo}/contributors", get_contributors, methods=["GET"])
router.add_api_route("/repos/{owner}/{repo}/branches", get_branches, methods=["GET"])
router.add_api_route("/repos/{owner}/{repo}/commits", get_commits, methods=["GET"])
router.add_api_route("/repos/{owner}/{repo}/releases", get_releases, methods=["GET"])
router.add_api_route("/repos/{owner}/{repo}/issues", get_issues, methods=["GET"])
router.add_api_route("/repos/{owner}/{repo}/pulls", get_pulls, methods=["GET"])
router.add_api_route("/repos/{owner}/{repo}/pulls/{pull_number}", get_pull, methods=["GET"])

router.add_api_route("/search/repositories", search_repositories, methods=["GET"])
router.add_api_route("/search/users", search_users, methods=["GET"])
