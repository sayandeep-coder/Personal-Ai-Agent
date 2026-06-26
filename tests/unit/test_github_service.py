"""GitHub service unit tests.

Purpose: verify GitHubService behavior including private-repo enforcement.
Responsibilities: cover public repo access, private repo rejection, auth errors, and rate limits.
Dependencies: GitHubService, FakeGitHubClient, ValidationException.
"""

import pytest

from core.exceptions import ValidationException
from services.github.service import GitHubService
from tests.unit.github_fakes import FakeGitHubClient


def _service(*, force_private: bool = False, force_401: bool = False, force_429: bool = False) -> GitHubService:
    return GitHubService(FakeGitHubClient(force_private=force_private, force_401=force_401, force_429=force_429))


# ── User tests ────────────────────────────────────────────────────────────────

def test_get_user_returns_normalized_profile() -> None:
    result = _service().get_user("octocat")
    assert result["login"] == "octocat"
    assert result["name"] == "The Octocat"
    assert "password" not in result
    assert "token" not in result


def test_get_user_repos_returns_list() -> None:
    result = _service().get_user_repos("octocat")
    assert isinstance(result, list)
    assert result[0]["name"] == "hello-world"


# ── Public repo tests ─────────────────────────────────────────────────────────

def test_get_repo_public_succeeds() -> None:
    result = _service().get_repo("octocat", "hello-world")
    assert result["name"] == "hello-world"
    assert result["private"] is False


def test_get_readme_public_repo_decodes_content() -> None:
    result = _service().get_readme("octocat", "hello-world")
    content = result["content"]
    assert isinstance(content, str)
    assert "Hello World" in content
    assert result["encoding"] == "base64"


def test_get_languages_returns_dict() -> None:
    result = _service().get_languages("octocat", "hello-world")
    assert "Python" in result


def test_get_contributors_returns_list() -> None:
    result = _service().get_contributors("octocat", "hello-world")
    assert result[0]["login"] == "octocat"
    assert result[0]["contributions"] == 99


def test_get_branches_returns_list() -> None:
    result = _service().get_branches("octocat", "hello-world")
    assert result[0]["name"] == "main"
    assert result[0]["sha"] == "abc123"


def test_get_commits_returns_list() -> None:
    result = _service().get_commits("octocat", "hello-world")
    assert result[0]["sha"] == "abc123"
    assert result[0]["message"] == "Initial commit"


def test_get_releases_returns_list() -> None:
    result = _service().get_releases("octocat", "hello-world")
    assert result[0]["tag_name"] == "v1.0.0"


def test_get_issues_returns_list_without_prs() -> None:
    result = _service().get_issues("octocat", "hello-world")
    assert result[0]["number"] == 1
    assert result[0]["title"] == "Bug report"


def test_get_pulls_returns_list() -> None:
    result = _service().get_pulls("octocat", "hello-world")
    assert result[0]["number"] == 5
    assert result[0]["head_branch"] == "feature/widget"


def test_get_pull_single_returns_normalized() -> None:
    result = _service().get_pull("octocat", "hello-world", 5)
    assert result["number"] == 5
    assert result["additions"] == 50


# ── Private repo enforcement — the critical tests ─────────────────────────────

def test_private_repo_get_repo_rejected() -> None:
    """_assert_public() fires on get_repo for a private repository."""
    with pytest.raises(ValidationException) as exc_info:
        _service(force_private=True).get_repo("corp", "secret")
    assert exc_info.value.code == "github.private_repository"


def test_private_repo_get_readme_rejected() -> None:
    """_check_public() fires before fetching README of a private repo."""
    with pytest.raises(ValidationException) as exc_info:
        _service(force_private=True).get_readme("corp", "secret")
    assert exc_info.value.code == "github.private_repository"


def test_private_repo_get_commits_rejected() -> None:
    """Commits endpoint is blocked for private repos."""
    with pytest.raises(ValidationException) as exc_info:
        _service(force_private=True).get_commits("corp", "secret")
    assert exc_info.value.code == "github.private_repository"


def test_private_repo_get_issues_rejected() -> None:
    """Issues endpoint is blocked for private repos."""
    with pytest.raises(ValidationException) as exc_info:
        _service(force_private=True).get_issues("corp", "secret")
    assert exc_info.value.code == "github.private_repository"


def test_private_repo_get_pulls_rejected() -> None:
    """PRs endpoint is blocked for private repos."""
    with pytest.raises(ValidationException) as exc_info:
        _service(force_private=True).get_pulls("corp", "secret")
    assert exc_info.value.code == "github.private_repository"


def test_private_repo_get_branches_rejected() -> None:
    """Branches endpoint is blocked for private repos."""
    with pytest.raises(ValidationException) as exc_info:
        _service(force_private=True).get_branches("corp", "secret")
    assert exc_info.value.code == "github.private_repository"


def test_private_repo_get_releases_rejected() -> None:
    """Releases endpoint is blocked for private repos."""
    with pytest.raises(ValidationException) as exc_info:
        _service(force_private=True).get_releases("corp", "secret")
    assert exc_info.value.code == "github.private_repository"


def test_private_repo_get_contributors_rejected() -> None:
    """Contributors endpoint is blocked for private repos."""
    with pytest.raises(ValidationException) as exc_info:
        _service(force_private=True).get_contributors("corp", "secret")
    assert exc_info.value.code == "github.private_repository"


def test_private_repo_get_languages_rejected() -> None:
    """Languages endpoint is blocked for private repos."""
    with pytest.raises(ValidationException) as exc_info:
        _service(force_private=True).get_languages("corp", "secret")
    assert exc_info.value.code == "github.private_repository"


def test_private_repo_get_pull_rejected() -> None:
    """Single PR endpoint is blocked for private repos."""
    with pytest.raises(ValidationException) as exc_info:
        _service(force_private=True).get_pull("corp", "secret", 1)
    assert exc_info.value.code == "github.private_repository"


# ── Error propagation tests ───────────────────────────────────────────────────

def test_invalid_token_propagates() -> None:
    """401 from GitHub surfaces as ValidationException with github.api_error code."""
    with pytest.raises(ValidationException) as exc_info:
        _service(force_401=True).get_user("octocat")
    assert exc_info.value.code == "github.api_error"
    assert exc_info.value.details is not None
    assert exc_info.value.details.get("github_status") == 401


def test_rate_limit_propagates() -> None:
    """429 from GitHub surfaces as ValidationException with github.api_error code."""
    with pytest.raises(ValidationException) as exc_info:
        _service(force_429=True).get_user("octocat")
    assert exc_info.value.code == "github.api_error"
    assert exc_info.value.details is not None
    assert exc_info.value.details.get("github_status") == 429


# ── Search tests ──────────────────────────────────────────────────────────────

def test_search_repositories_filters_private() -> None:
    """search_repositories strips private repos from results."""
    result = _service().search_repositories("hello")
    assert isinstance(result["items"], list)
    for item in result["items"]:
        assert not item.get("private")


def test_search_users_returns_results() -> None:
    result = _service().search_users("octocat")
    assert result["total_count"] == 1
    items = result["items"]
    assert isinstance(items, list)
    assert isinstance(items[0], dict)
    assert items[0]["login"] == "octocat"
