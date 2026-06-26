"""Google Docs service wrapper.

Purpose: provide Docs API operations.
Responsibilities: create, read, append text, replace text, batch update.
Dependencies: Google credentials and REST client protocol.
Extension Notes: preserve document semantics in higher-level services.
"""

from core.exceptions import ValidationException
from integrations.google.common.http import GoogleApiPort, JsonDict
from services.google.docs.normalizer import document, document_files
from services.google.protocols import AccessTokenProvider

BASE = "https://docs.googleapis.com/v1/documents"
DRIVE = "https://www.googleapis.com/drive/v3/files"
DOC_MIME = "application/vnd.google-apps.document"

# Maps user-facing format names to the MIME types accepted by the Drive export API.
# Reference: https://developers.google.com/drive/api/guides/ref-export-formats
_DOC_EXPORT_MIME: dict[str, str] = {
    "pdf":      "application/pdf",
    "docx":     "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "odt":      "application/vnd.oasis.opendocument.text",
    "html":     "text/html",
    "txt":      "text/plain",
    "markdown": "text/markdown",
    "epub":     "application/epub+zip",
}

_DOC_FILENAME_EXT: dict[str, str] = {
    "pdf": "pdf", "docx": "docx", "odt": "odt",
    "html": "html", "txt": "txt", "markdown": "md", "epub": "epub",
}


class DocsService:
    """Service wrapper for Google Docs APIs."""

    def __init__(self, credentials: AccessTokenProvider, client: GoogleApiPort) -> None:
        """Create a Docs service."""
        self._credentials = credentials
        self._client = client

    def create_document(self, email: str, title: str, content: str = "") -> JsonDict:
        """Create a Google document."""
        created = self._client.post(BASE, self._token(email), {"title": title})
        doc_id = str(created.get("documentId") or created.get("id", ""))
        if content and doc_id:
            self.append_text(email, doc_id, content)
        return document(created)

    def read_document(self, email: str, document_id: str) -> JsonDict:
        """Read a normalized Google document."""
        return document(self._client.get(f"{BASE}/{document_id}", self._token(email)))

    def list_documents(
        self,
        email: str,
        page_token: str | None = None,
        max_results: int = 25,
    ) -> JsonDict:
        """List available Google Docs."""
        params: JsonDict = {"q": f"mimeType = '{DOC_MIME}'", "pageSize": max_results}
        params["fields"] = "nextPageToken,files(id,name,createdTime,modifiedTime)"
        if page_token:
            params["pageToken"] = page_token
        return document_files(self._client.get(DRIVE, self._token(email), params))

    def append_text(self, email: str, document_id: str, text: str) -> JsonDict:
        """Append text to a document."""
        return self.batch_update(
            email,
            document_id,
            {"requests": [{"insertText": {"location": {"index": 1}, "text": text}}]},
        )

    def replace_text(self, email: str, document_id: str, old: str, new: str) -> JsonDict:
        """Replace text in a document."""
        request = {"replaceAllText": {"containsText": {"text": old}, "replaceText": new}}
        return self.batch_update(email, document_id, {"requests": [request]})

    def batch_update(self, email: str, document_id: str, payload: JsonDict) -> JsonDict:
        """Run a Docs batch update."""
        result = self._client.post(f"{BASE}/{document_id}:batchUpdate", self._token(email), payload)
        return {"document_id": document_id, "updated": True, "replies": result.get("replies", [])}

    def export_document(self, email: str, document_id: str, fmt: str) -> tuple[bytes, str, str]:
        """Export a document as binary and return (bytes, content_type, filename).

        fmt must be one of the keys in _DOC_EXPORT_MIME.
        Uses the Drive export API which is the only way to convert Google Docs
        native format to PDF/DOCX/etc.
        """
        fmt = fmt.lower()
        if fmt not in _DOC_EXPORT_MIME:
            raise ValidationException(
                f"Unsupported export format {fmt!r}. "
                f"Supported: {', '.join(sorted(_DOC_EXPORT_MIME))}.",
                code="docs.unsupported_export_format",
            )
        mime = _DOC_EXPORT_MIME[fmt]
        ext = _DOC_FILENAME_EXT[fmt]
        # Fetch document title so the downloaded filename is meaningful
        try:
            meta = self._client.get(f"{DRIVE}/{document_id}", self._token(email), {"fields": "name"})
            title = str(meta.get("name", document_id))
        except Exception:
            title = document_id
        raw, content_type = self._client.get_raw(
            f"{DRIVE}/{document_id}/export",
            self._token(email),
            {"mimeType": mime},
        )
        filename = f"{title}.{ext}"
        return raw, content_type or mime, filename

    def metadata(self, email: str, document_id: str) -> JsonDict:
        """Return document metadata."""
        doc = self.read_document(email, document_id)
        return {key: doc.get(key) for key in ("id", "title", "word_count")}

    def _token(self, email: str) -> str:
        """Return access token for user email."""
        return self._credentials.access_token(email)
