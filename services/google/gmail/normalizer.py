"""Gmail response normalization.

Purpose: convert Gmail API payloads into stable application contracts.
Responsibilities: expose safe message, label, and unread structures.
Dependencies: Gmail parsing helpers.
Extension Notes: add thread summaries without changing API route contracts.
"""

from integrations.google.common.http import JsonDict
from services.google.gmail.parsing import attachments, bodies, header


def message_summary(message: JsonDict) -> dict[str, object]:
    """Return a simplified Gmail message summary."""
    payload = message.get("payload", {})
    payload = payload if isinstance(payload, dict) else {}
    labels = _labels(message)
    return {
        "id": message.get("id", ""),
        "thread_id": message.get("threadId", ""),
        "subject": header(payload, "Subject"),
        "from": header(payload, "From"),
        "to": header(payload, "To"),
        "date": header(payload, "Date"),
        "labels": labels,
        "snippet": message.get("snippet", ""),
        "unread": "UNREAD" in labels,
        "has_attachments": bool(attachments(payload)),
    }


def message_detail(message: JsonDict) -> dict[str, object]:
    """Return a simplified Gmail message with decoded body content."""
    payload = message.get("payload", {})
    payload = payload if isinstance(payload, dict) else {}
    text, html = bodies(payload)
    return {
        **message_summary(message),
        "cc": header(payload, "Cc"),
        "bcc": header(payload, "Bcc"),
        "body_text": text,
        "body_html": html,
        "attachments": attachments(payload),
    }


def labels(payload: JsonDict) -> list[dict[str, object]]:
    """Return simplified Gmail labels."""
    raw = payload.get("labels", [])
    raw = raw if isinstance(raw, list) else []
    return [
        {"id": item.get("id", ""), "name": item.get("name", ""), "type": item.get("type", "")}
        for item in raw
        if isinstance(item, dict)
    ]


def _labels(message: JsonDict) -> list[str]:
    """Return label IDs from a message."""
    raw = message.get("labelIds", [])
    return [str(item) for item in raw] if isinstance(raw, list) else []
