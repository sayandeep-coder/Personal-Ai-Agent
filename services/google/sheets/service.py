"""Google Sheets service wrapper.

Purpose: provide Sheets API operations.
Responsibilities: create, read, update cells, append rows, batch update.
Dependencies: Google credentials and REST client protocol.
Extension Notes: validation of business ranges belongs above this wrapper.
"""

from urllib.parse import quote

from core.exceptions import ValidationException
from integrations.google.common.http import GoogleApiPort, JsonDict
from services.google.sheets.normalizer import spreadsheet, spreadsheet_files, update_result
from services.google.protocols import AccessTokenProvider

BASE = "https://sheets.googleapis.com/v4/spreadsheets"
DRIVE = "https://www.googleapis.com/drive/v3/files"
EXPORT = "https://docs.google.com/spreadsheets/d"
SHEET_MIME = "application/vnd.google-apps.spreadsheet"

# Maps user-facing format names → (Drive export mimeType, file extension, content-type)
_SHEET_EXPORT: dict[str, tuple[str, str, str]] = {
    "xlsx": (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ),
    "csv": ("text/csv", "csv", "text/csv"),
    "tsv": ("text/tab-separated-values", "tsv", "text/tab-separated-values"),
    "pdf": ("application/pdf", "pdf", "application/pdf"),
    "ods": ("application/x-vnd.oasis.opendocument.spreadsheet", "ods", "application/x-vnd.oasis.opendocument.spreadsheet"),
}


def _encode_range(cell_range: str) -> str:
    """Percent-encode a Sheets A1 range for safe URL embedding.

    Sheet names containing spaces (e.g. 'June 2026') would otherwise produce
    an InvalidURL error in Python's urllib because spaces are control chars in
    HTTP/1.1 request lines.
    """
    return quote(cell_range, safe="!:")


class SheetsService:
    """Service wrapper for Google Sheets APIs."""

    def __init__(self, credentials: AccessTokenProvider, client: GoogleApiPort) -> None:
        """Create a Sheets service."""
        self._credentials = credentials
        self._client = client

    def create_spreadsheet(self, email: str, title: str, worksheet: str = "Sheet1") -> JsonDict:
        """Create a spreadsheet."""
        payload: JsonDict = {"properties": {"title": title}, "sheets": [{"properties": {"title": worksheet}}]}
        return spreadsheet(self._client.post(BASE, self._token(email), payload))

    def read_spreadsheet(self, email: str, spreadsheet_id: str, cell_range: str = "A1:Z100") -> JsonDict:
        """Read spreadsheet metadata."""
        meta = self._client.get(f"{BASE}/{spreadsheet_id}", self._token(email))
        values = self.read_range(email, spreadsheet_id, cell_range)
        return spreadsheet(meta, values)

    def list_spreadsheets(
        self,
        email: str,
        page_token: str | None = None,
        max_results: int = 25,
    ) -> JsonDict:
        """List available Google Sheets."""
        params: JsonDict = {"q": f"mimeType = '{SHEET_MIME}'", "pageSize": max_results}
        params["fields"] = "nextPageToken,files(id,name,createdTime,modifiedTime)"
        if page_token:
            params["pageToken"] = page_token
        return spreadsheet_files(self._client.get(DRIVE, self._token(email), params))

    def read_range(self, email: str, spreadsheet_id: str, cell_range: str) -> JsonDict:
        """Read spreadsheet range values."""
        return self._client.get(f"{BASE}/{spreadsheet_id}/values/{_encode_range(cell_range)}", self._token(email))

    def update_cells(
        self,
        email: str,
        spreadsheet_id: str,
        cell_range: str,
        values: list[list[object]],
    ) -> JsonDict:
        """Update cells in a spreadsheet."""
        url = f"{BASE}/{spreadsheet_id}/values/{_encode_range(cell_range)}?valueInputOption=USER_ENTERED"
        result = self._client.patch(url, self._token(email), {"values": values})
        return update_result(result)

    def append_rows(
        self,
        email: str,
        spreadsheet_id: str,
        cell_range: str,
        values: list[list[object]],
    ) -> JsonDict:
        """Append rows to a spreadsheet."""
        url = f"{BASE}/{spreadsheet_id}/values/{_encode_range(cell_range)}:append?valueInputOption=USER_ENTERED"
        result = self._client.post(url, self._token(email), {"values": values})
        return update_result(result)

    def batch_update(self, email: str, spreadsheet_id: str, payload: JsonDict) -> JsonDict:
        """Run a Sheets batch update."""
        result = self._client.post(f"{BASE}/{spreadsheet_id}:batchUpdate", self._token(email), payload)
        return {"updated": True, "replies": result.get("replies", [])}

    def export_spreadsheet(self, email: str, spreadsheet_id: str, fmt: str) -> tuple[bytes, str, str]:
        """Export a spreadsheet as binary and return (bytes, content_type, filename).

        fmt must be one of: xlsx, csv, tsv, pdf, ods.
        Uses the Drive export API which converts the native Google Sheets format.
        """
        fmt = fmt.lower()
        if fmt not in _SHEET_EXPORT:
            raise ValidationException(
                f"Unsupported export format {fmt!r}. "
                f"Supported: {', '.join(sorted(_SHEET_EXPORT))}.",
                code="sheets.unsupported_export_format",
            )
        mime, ext, content_type = _SHEET_EXPORT[fmt]
        try:
            meta = self._client.get(f"{DRIVE}/{spreadsheet_id}", self._token(email), {"fields": "name"})
            title = str(meta.get("name", spreadsheet_id))
        except Exception:
            title = spreadsheet_id
        raw, ct = self._client.get_raw(
            f"{DRIVE}/{spreadsheet_id}/export",
            self._token(email),
            {"mimeType": mime},
        )
        filename = f"{title}.{ext}"
        return raw, ct or content_type, filename

    def worksheet_metadata(self, email: str, spreadsheet_id: str) -> JsonDict:
        """Return worksheet metadata."""
        sheet = self.read_spreadsheet(email, spreadsheet_id)
        return {"id": sheet.get("id"), "worksheets": sheet.get("worksheets", [])}

    def _token(self, email: str) -> str:
        """Return access token for user email."""
        return self._credentials.access_token(email)
