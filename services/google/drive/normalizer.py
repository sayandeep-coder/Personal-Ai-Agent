"""Drive response normalization.

Purpose: convert Drive API payloads into stable file contracts.
Responsibilities: simplify metadata and pagination responses.
Dependencies: Google Drive JSON shapes.
Extension Notes: add shared-drive ownership fields when needed.
"""

from integrations.google.common.http import JsonDict


def file_item(item: JsonDict) -> dict[str, object]:
    """Return normalized Drive file metadata."""
    owners = item.get("owners", [])
    owners = owners if isinstance(owners, list) else []
    owner = owners[0].get("emailAddress") if owners and isinstance(owners[0], dict) else None
    mime = str(item.get("mimeType", ""))
    size = item.get("size", 0)
    return {
        "id": item.get("id", ""),
        "name": item.get("name", ""),
        "mime_type": mime,
        "size": int(size) if isinstance(size, int | str) else 0,
        "owner": owner,
        "created_at": item.get("createdTime"),
        "modified_at": item.get("modifiedTime"),
        "download_url": item.get("webContentLink"),
        "thumbnail": item.get("thumbnailLink"),
        "folder": mime == "application/vnd.google-apps.folder",
    }


def file_page(payload: JsonDict) -> dict[str, object]:
    """Return a normalized page of Drive files."""
    files = payload.get("files", [])
    files = files if isinstance(files, list) else []
    return {
        "files": [file_item(item) for item in files if isinstance(item, dict)],
        "next_page_token": payload.get("nextPageToken"),
    }
