"""Gmail payload parsing helpers.

Purpose: normalize Gmail MIME payloads into safe response fields.
Responsibilities: decode bodies, extract headers, and flatten attachments.
Dependencies: base64 and Google JSON shapes.
Extension Notes: add charset-aware MIME decoding if Gmail edge cases require it.
"""

from base64 import urlsafe_b64decode

from integrations.google.common.http import JsonDict


def header(payload: JsonDict, name: str) -> str | None:
    """Return a message header by case-insensitive name."""
    headers = payload.get("headers", [])
    if not isinstance(headers, list):
        return None
    for item in headers:
        if isinstance(item, dict) and str(item.get("name", "")).lower() == name.lower():
            return str(item.get("value", ""))
    return None


def decode_body(data: object) -> str:
    """Decode Gmail base64url body data."""
    if not isinstance(data, str) or not data:
        return ""
    padded = data + "=" * (-len(data) % 4)
    return urlsafe_b64decode(padded.encode()).decode(errors="replace")


def walk_parts(part: JsonDict) -> list[JsonDict]:
    """Return a flattened list of message MIME parts."""
    parts = [part]
    children = part.get("parts", [])
    children = children if isinstance(children, list) else []
    for child in children:
        if isinstance(child, dict):
            parts.extend(walk_parts(child))
    return parts


def bodies(payload: JsonDict) -> tuple[str, str]:
    """Return decoded text and HTML bodies."""
    text, html = "", ""
    for part in walk_parts(payload):
        mime = str(part.get("mimeType", ""))
        body = part.get("body", {})
        data = body.get("data") if isinstance(body, dict) else None
        if mime == "text/plain" and not text:
            text = decode_body(data)
        if mime == "text/html" and not html:
            html = decode_body(data)
    return text, html


def attachments(payload: JsonDict) -> list[dict[str, object]]:
    """Return simplified attachment metadata."""
    values: list[dict[str, object]] = []
    for part in walk_parts(payload):
        filename = part.get("filename")
        body = part.get("body", {})
        if filename and isinstance(body, dict):
            values.append(
                {
                    "filename": str(filename),
                    "mime_type": str(part.get("mimeType", "")),
                    "size": int(body.get("size", 0) or 0),
                    "attachment_id": body.get("attachmentId"),
                }
            )
    return values
