"""GitHub API response normalizers.

Purpose: convert raw GitHub API payloads into stable, typed application contracts.
Responsibilities: extract only the fields the application exposes; drop everything else.
Dependencies: none — pure data transformation.
Extension Notes: add new normalizers alongside new endpoints; never mutate inputs.
"""

from integrations.github.protocols import JsonDict


def user_profile(raw: JsonDict) -> JsonDict:
    """Normalize a GitHub user object."""
    return {
        "login": raw.get("login"),
        "name": raw.get("name"),
        "bio": raw.get("bio"),
        "avatar_url": raw.get("avatar_url"),
        "html_url": raw.get("html_url"),
        "public_repos": raw.get("public_repos"),
        "followers": raw.get("followers"),
        "following": raw.get("following"),
        "created_at": raw.get("created_at"),
        "updated_at": raw.get("updated_at"),
        "location": raw.get("location"),
        "company": raw.get("company"),
        "blog": raw.get("blog"),
        "twitter_username": raw.get("twitter_username"),
    }


def repository(raw: JsonDict) -> JsonDict:
    """Normalize a GitHub repository object."""
    license_raw = raw.get("license")
    license_name = license_raw.get("name") if isinstance(license_raw, dict) else None
    owner_raw = raw.get("owner")
    owner_login = owner_raw.get("login") if isinstance(owner_raw, dict) else None
    return {
        "id": raw.get("id"),
        "name": raw.get("name"),
        "full_name": raw.get("full_name"),
        "owner": owner_login,
        "description": raw.get("description"),
        "html_url": raw.get("html_url"),
        "clone_url": raw.get("clone_url"),
        "language": raw.get("language"),
        "stars": raw.get("stargazers_count"),
        "forks": raw.get("forks_count"),
        "watchers": raw.get("watchers_count"),
        "open_issues": raw.get("open_issues_count"),
        "license": license_name,
        "topics": raw.get("topics", []),
        "default_branch": raw.get("default_branch"),
        "created_at": raw.get("created_at"),
        "updated_at": raw.get("updated_at"),
        "pushed_at": raw.get("pushed_at"),
        "size": raw.get("size"),
        "archived": raw.get("archived"),
        "disabled": raw.get("disabled"),
        "visibility": raw.get("visibility"),
        "private": raw.get("private"),
    }


def commit(raw: JsonDict) -> JsonDict:
    """Normalize a GitHub commit list entry."""
    commit_data = raw.get("commit", {})
    commit_data = commit_data if isinstance(commit_data, dict) else {}
    author_data = commit_data.get("author", {})
    author_data = author_data if isinstance(author_data, dict) else {}
    committer_data = commit_data.get("committer", {})
    committer_data = committer_data if isinstance(committer_data, dict) else {}
    gh_author = raw.get("author")
    return {
        "sha": raw.get("sha"),
        "message": commit_data.get("message"),
        "author_name": author_data.get("name"),
        "author_email": author_data.get("email"),
        "author_date": author_data.get("date"),
        "committer_name": committer_data.get("name"),
        "committer_date": committer_data.get("date"),
        "github_login": gh_author.get("login") if isinstance(gh_author, dict) else None,
        "html_url": raw.get("html_url"),
    }


def branch(raw: JsonDict) -> JsonDict:
    """Normalize a GitHub branch entry."""
    commit_raw = raw.get("commit", {})
    commit_raw = commit_raw if isinstance(commit_raw, dict) else {}
    return {
        "name": raw.get("name"),
        "sha": commit_raw.get("sha"),
        "protected": raw.get("protected"),
    }


def release(raw: JsonDict) -> JsonDict:
    """Normalize a GitHub release entry."""
    author_raw = raw.get("author", {})
    author_raw = author_raw if isinstance(author_raw, dict) else {}
    return {
        "id": raw.get("id"),
        "tag_name": raw.get("tag_name"),
        "name": raw.get("name"),
        "body": raw.get("body"),
        "draft": raw.get("draft"),
        "prerelease": raw.get("prerelease"),
        "created_at": raw.get("created_at"),
        "published_at": raw.get("published_at"),
        "html_url": raw.get("html_url"),
        "author": author_raw.get("login"),
    }


def issue(raw: JsonDict) -> JsonDict:
    """Normalize a GitHub issue (skips pull requests mixed into /issues)."""
    user_raw = raw.get("user", {})
    user_raw = user_raw if isinstance(user_raw, dict) else {}
    labels_raw = raw.get("labels", [])
    labels_list = labels_raw if isinstance(labels_raw, list) else []
    label_names = [lbl.get("name") for lbl in labels_list if isinstance(lbl, dict)]
    return {
        "number": raw.get("number"),
        "title": raw.get("title"),
        "state": raw.get("state"),
        "body": raw.get("body"),
        "user": user_raw.get("login"),
        "labels": label_names,
        "created_at": raw.get("created_at"),
        "updated_at": raw.get("updated_at"),
        "closed_at": raw.get("closed_at"),
        "html_url": raw.get("html_url"),
        "comments": raw.get("comments"),
    }


def pull_request(raw: JsonDict) -> JsonDict:
    """Normalize a GitHub pull request entry."""
    user_raw = raw.get("user", {})
    user_raw = user_raw if isinstance(user_raw, dict) else {}
    head_raw = raw.get("head", {})
    head_raw = head_raw if isinstance(head_raw, dict) else {}
    base_raw = raw.get("base", {})
    base_raw = base_raw if isinstance(base_raw, dict) else {}
    return {
        "number": raw.get("number"),
        "title": raw.get("title"),
        "state": raw.get("state"),
        "body": raw.get("body"),
        "user": user_raw.get("login"),
        "head_branch": head_raw.get("ref"),
        "base_branch": base_raw.get("ref"),
        "draft": raw.get("draft"),
        "merged": raw.get("merged"),
        "merged_at": raw.get("merged_at"),
        "created_at": raw.get("created_at"),
        "updated_at": raw.get("updated_at"),
        "closed_at": raw.get("closed_at"),
        "html_url": raw.get("html_url"),
        "commits": raw.get("commits"),
        "additions": raw.get("additions"),
        "deletions": raw.get("deletions"),
        "changed_files": raw.get("changed_files"),
    }


def contributor(raw: JsonDict) -> JsonDict:
    """Normalize a GitHub contributor entry."""
    return {
        "login": raw.get("login"),
        "avatar_url": raw.get("avatar_url"),
        "html_url": raw.get("html_url"),
        "contributions": raw.get("contributions"),
        "type": raw.get("type"),
    }


def readme(raw: JsonDict) -> JsonDict:
    """Normalize a GitHub README content response."""
    import base64 as _b64
    encoded = raw.get("content", "")
    content = ""
    if isinstance(encoded, str) and encoded:
        try:
            content = _b64.b64decode(encoded.replace("\n", "")).decode("utf-8")
        except Exception:
            content = encoded
    return {
        "name": raw.get("name"),
        "path": raw.get("path"),
        "encoding": raw.get("encoding"),
        "html_url": raw.get("html_url"),
        "content": content,
    }


def search_repositories(raw: JsonDict) -> JsonDict:
    """Normalize a GitHub repository search result."""
    items = raw.get("items", [])
    items = items if isinstance(items, list) else []
    return {
        "total_count": raw.get("total_count"),
        "incomplete_results": raw.get("incomplete_results"),
        "items": [repository(item) for item in items if isinstance(item, dict)],
    }


def search_users(raw: JsonDict) -> JsonDict:
    """Normalize a GitHub user search result."""
    items = raw.get("items", [])
    items = items if isinstance(items, list) else []
    return {
        "total_count": raw.get("total_count"),
        "incomplete_results": raw.get("incomplete_results"),
        "items": [
            {
                "login": item.get("login"),
                "avatar_url": item.get("avatar_url"),
                "html_url": item.get("html_url"),
                "type": item.get("type"),
                "score": item.get("score"),
            }
            for item in items
            if isinstance(item, dict)
        ],
    }
