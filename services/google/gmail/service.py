"""Gmail service wrapper.

Purpose: provide production Gmail API operations.
Responsibilities: list, read, search messages, labels, threads, metadata.
Dependencies: Google credentials and REST client protocol.
Extension Notes: add batching only after usage patterns require it.
"""

from integrations.google.common.http import GoogleApiPort, JsonDict
from core.logging import get_logger
from services.google.gmail.normalizer import labels as normalize_labels
from services.google.gmail.normalizer import message_detail
from services.google.gmail.pages import message_page
from services.google.gmail.send import AttachmentSpec, raw_message
from services.google.protocols import AccessTokenProvider

BASE = "https://gmail.googleapis.com/gmail/v1/users/me"
GMAIL_SEND_SCOPE = "https://www.googleapis.com/auth/gmail.send"

_logger = get_logger(__name__)


class GmailService:
    """Service wrapper for Gmail APIs."""

    def __init__(self, credentials: AccessTokenProvider, client: GoogleApiPort) -> None:
        """Create a Gmail service."""
        self._credentials = credentials
        self._client = client

    def list_messages(
        self,
        email: str,
        page_token: str | None = None,
        max_results: int = 10,
    ) -> JsonDict:
        """List normalized Gmail message summaries with pagination."""
        params: JsonDict = {"maxResults": max_results}
        if page_token:
            params["pageToken"] = page_token
        listing = self._client.get(f"{BASE}/messages", self._token(email), params)
        return message_page(listing, lambda message_id: self._raw_message(email, message_id))

    def get_message(self, email: str, message_id: str) -> JsonDict:
        """Return a normalized Gmail message."""
        return message_detail(self._raw_message(email, message_id))

    def search_messages(
        self,
        email: str,
        query: str,
        max_results: int = 10,
        page_token: str | None = None,
    ) -> JsonDict:
        """Search Gmail messages and return normalized summaries."""
        params: JsonDict = {"q": query, "maxResults": max_results}
        if page_token:
            params["pageToken"] = page_token
        listing = self._client.get(
            f"{BASE}/messages",
            self._token(email),
            params,
        )
        return message_page(listing, lambda message_id: self._raw_message(email, message_id))

    def unread_count(self, email: str) -> int:
        """Return unread message count."""
        result = self.search_messages(email, "is:unread", 1)
        value = result.get("result_size_estimate", 0)
        return int(value) if isinstance(value, int | str) else 0

    def labels(self, email: str) -> JsonDict:
        """Return normalized Gmail labels."""
        payload = self._client.get(f"{BASE}/labels", self._token(email))
        return {"labels": normalize_labels(payload)}

    def send_message(
        self,
        email: str,
        recipients: list[str],
        subject: str,
        body_text: str,
        body_html: str | None = None,
        cc: list[str] | None = None,
        bcc: list[str] | None = None,
        attachments: list[AttachmentSpec] | None = None,
    ) -> JsonDict:
        """Send an email and return normalized send metadata."""
        _logger.warning(
            "gmail_send_attempt",
            sender=email,
            recipient_count=len(recipients),
            cc_count=len(cc or []),
            bcc_count=len(bcc or []),
            subject=subject,
            has_html=body_html is not None,
            attachment_count=len(attachments or []),
        )
        token = self._token(email, required_scopes=[GMAIL_SEND_SCOPE])
        raw = raw_message(email, recipients, subject, body_text, body_html, cc, bcc, attachments)
        result = self._client.post(f"{BASE}/messages/send", token, {"raw": raw})
        _logger.warning(
            "gmail_send_success",
            sender=email,
            message_id=result.get("id"),
            thread_id=result.get("threadId"),
        )
        return {"id": result.get("id", ""), "thread_id": result.get("threadId", ""), "sent": True}

    def threads(self, email: str, page_token: str | None = None) -> JsonDict:
        """Return Gmail threads."""
        params: JsonDict = {}
        if page_token:
            params["pageToken"] = page_token
        return self._client.get(f"{BASE}/threads", self._token(email), params)

    def attachment_metadata(self, email: str, message_id: str) -> list[JsonDict]:
        """Return attachment metadata from a message payload."""
        message = self.get_message(email, message_id)
        items = message.get("attachments", [])
        items = items if isinstance(items, list) else []
        return [item for item in items if isinstance(item, dict)]

    def _raw_message(self, email: str, message_id: str) -> JsonDict:
        """Return a raw Gmail message for internal normalization."""
        return self._client.get(f"{BASE}/messages/{message_id}", self._token(email))

    def _token(self, email: str, required_scopes: list[str] | None = None) -> str:
        """Return access token for user email, optionally verifying scopes."""
        return self._credentials.access_token(email, required_scopes)
