"""Docs response normalization.

Purpose: convert Google Docs documents into readable contracts.
Responsibilities: extract text, metadata, and word counts.
Dependencies: Google Docs JSON shapes.
Extension Notes: preserve richer structural elements for editor features later.
"""

from integrations.google.common.http import JsonDict


def document(payload: JsonDict) -> dict[str, object]:
    """Return a normalized document."""
    content = _content(payload)
    document_id = str(payload.get("documentId", ""))
    return {
        "id": document_id,
        "title": payload.get("title", ""),
        "url": _url(document_id),
        "content": content,
        "created_at": payload.get("createdTime"),
        "updated_at": payload.get("modifiedTime"),
        "owner": payload.get("owner"),
        "word_count": len(content.split()),
    }


def document_files(payload: JsonDict) -> dict[str, object]:
    """Return normalized available Google Docs."""
    files = payload.get("files", [])
    files = files if isinstance(files, list) else []
    return {"documents": [_file(item) for item in files if isinstance(item, dict)], "next_page_token": payload.get("nextPageToken")}


def _file(item: JsonDict) -> dict[str, object]:
    """Return a normalized document file entry."""
    document_id = str(item.get("id", ""))
    return {
        "id": document_id,
        "title": item.get("name", ""),
        "url": _url(document_id),
        "created_at": item.get("createdTime"),
        "updated_at": item.get("modifiedTime"),
    }


def _url(document_id: str) -> str | None:
    """Return the browser URL for a Google Doc."""
    return f"https://docs.google.com/document/d/{document_id}/edit" if document_id else None


def _content(payload: JsonDict) -> str:
    """Extract plain text from a Docs body."""
    body = payload.get("body", {})
    content = body.get("content", []) if isinstance(body, dict) else []
    chunks: list[str] = []
    for item in content:
        paragraph = item.get("paragraph") if isinstance(item, dict) else None
        elements = paragraph.get("elements", []) if isinstance(paragraph, dict) else []
        for element in elements:
            run = element.get("textRun") if isinstance(element, dict) else None
            if isinstance(run, dict):
                chunks.append(str(run.get("content", "")))
    return "".join(chunks).strip()
