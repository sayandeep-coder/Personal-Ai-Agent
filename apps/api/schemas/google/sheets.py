"""Sheets API schemas.

Purpose: validate spreadsheet creation and update requests.
Responsibilities: model worksheet selection and row/cell operations.
Dependencies: Pydantic v2.
Extension Notes: add typed table schemas once domain tables exist.
"""

from enum import StrEnum

from pydantic import BaseModel, EmailStr, Field, field_validator

_ALLOWED_SHARE_ROLES = {"writer", "commenter", "reader"}


class SheetOperation(StrEnum):
    """Supported spreadsheet update operations."""

    APPEND = "append"
    REPLACE = "replace"
    UPDATE = "update"
    BATCH = "batch"


class ShareEntry(BaseModel):
    """A single sharing permission entry."""

    email: EmailStr
    role: str = Field("reader", examples=["writer", "reader", "commenter"])

    @field_validator("role")
    @classmethod
    def role_must_be_allowed(cls, v: str) -> str:
        if v not in _ALLOWED_SHARE_ROLES:
            raise ValueError(f"role {v!r} is not allowed; use one of: {', '.join(sorted(_ALLOWED_SHARE_ROLES))}")
        return v


class CreateSpreadsheetRequest(BaseModel):
    """Create spreadsheet request."""

    email: EmailStr = Field(..., examples=["user@example.com"])
    title: str = Field(..., examples=["Expenses"])
    worksheet: str = Field("Sheet1", examples=["June 2026"])
    headers: list[str] = Field(default_factory=list, examples=[["Date", "Amount", "Category"]])
    rows: list[list[object]] = Field(default_factory=list, description="Data rows to append after headers")
    freeze_header: bool = Field(False, description="Freeze the first header row")
    auto_resize_columns: bool = Field(False, description="Auto-resize all columns after writing")
    create_chart: bool = Field(False, description="Create a basic column chart from the data (best-effort)")
    theme: str | None = Field(None, description="Named colour theme to apply (e.g. 'modern_blue')")
    share_with: list[str | ShareEntry] = Field(default_factory=list, description="Email addresses or share entries to grant access")


class UpdateSpreadsheetRequest(BaseModel):
    """Update spreadsheet request."""

    email: EmailStr = Field(..., examples=["user@example.com"])
    operation: SheetOperation = SheetOperation.APPEND
    worksheet: str = Field("Sheet1", examples=["June"])
    range: str = Field("A1", examples=["A1:C10"])
    values: list[list[object]] = Field(default_factory=list)
    requests: list[dict[str, object]] = Field(default_factory=list)

    def a1_range(self) -> str:
        """Return worksheet-qualified A1 range."""
        return f"{self.worksheet}!{self.range}" if "!" not in self.range else self.range
