"""Google service test fakes.

Purpose: provide reusable fake credentials and API client.
Responsibilities: capture requests and return deterministic payloads.
Dependencies: Google service protocol shapes.
Extension Notes: add error simulation as integration policies grow.
"""

from integrations.google.common.http import JsonDict
from tests.unit import google_payloads as payloads


class Credentials:
    """Fake credential resolver."""

    def access_token(self, email: str, required_scopes: list[str] | None = None) -> str:
        """Return fake token."""
        if email == "expired@example.com":
            from core.exceptions import ValidationException

            raise ValidationException("expired", code="google.token_expired")
        return "token"


class Client:
    """Fake Google API client."""

    def __init__(self) -> None:
        """Create fake client."""
        self.calls: list[tuple[str, str, JsonDict | None]] = []

    def get(self, url: str, token: str, params: JsonDict | None = None) -> JsonDict:
        """Capture GET."""
        self.calls.append(("GET", url, params))
        if url.endswith("/messages"):
            return {"messages": [{"id": "m1"}], "resultSizeEstimate": 2}
        if "/messages/" in url:
            return payloads.gmail_message()
        if url.endswith("/labels"):
            return {"labels": [{"id": "INBOX", "name": "Inbox", "type": "system"}]}
        if "/drive/v3/files" in url:
            query = str((params or {}).get("q", ""))
            if "document" in query:
                return {"files": [payloads.doc_file()]}
            if "spreadsheet" in query:
                return {"files": [payloads.sheet_file()]}
            return {"files": [payloads.drive_file()]} if url.endswith("/files") else payloads.drive_file()
        if "docs.googleapis.com" in url:
            return payloads.doc()
        if "sheets.googleapis.com" in url and "/values/" in url:
            return {"values": [["Date", "Amount"], ["2026-06-30", 10]]}
        if "sheets.googleapis.com" in url:
            return payloads.sheet()
        if "calendar/v3" in url:
            return {"items": [payloads.event()]}
        return {"url": url, "params": params or {}, "resultSizeEstimate": 2}

    def post(self, url: str, token: str, payload: JsonDict | None = None) -> JsonDict:
        """Capture POST."""
        self.calls.append(("POST", url, payload))
        if "gmail" in url and url.endswith("/messages/send"):
            return {"id": "sent-message", "threadId": "sent-thread"}
        if "calendar" in url:
            return {"id": "evt", **(payload or {})}
        if "drive" in url:
            return payloads.drive_file()
        if "documents" in url and ":batchUpdate" not in url:
            return {"documentId": "doc", "title": (payload or {}).get("title", "")}
        if "spreadsheets" in url and ":batchUpdate" not in url and "/values/" not in url:
            return payloads.sheet()
        if "/values/" in url:
            return {"updatedRange": "A1", "updatedRows": 1, "updatedCells": 1}
        return {"url": url, "payload": payload or {}}

    def patch(self, url: str, token: str, payload: JsonDict) -> JsonDict:
        """Capture PATCH."""
        self.calls.append(("PATCH", url, payload))
        if "calendar" in url:
            return {"id": "evt", **payload}
        if "/values/" in url:
            return {"updatedRange": "A1", "updatedRows": 1, "updatedCells": 1}
        return {"url": url, "payload": payload}

    def get_raw(self, url: str, token: str, params: JsonDict | None = None) -> tuple[bytes, str]:
        """Capture raw GET — return deterministic binary payload."""
        self.calls.append(("GET_RAW", url, params))
        mime = str((params or {}).get("mimeType", "application/octet-stream"))
        return b"fake-binary-content", mime

    def delete(self, url: str, token: str) -> JsonDict:
        """Capture DELETE."""
        self.calls.append(("DELETE", url, None))
        return {"url": url, "deleted": True}
