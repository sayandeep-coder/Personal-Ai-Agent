"""Weather API schemas.

Purpose: validate Weather API query parameters.
Responsibilities: define units and reusable city query validation.
Dependencies: Pydantic v2 and Python enums.
Extension Notes: add coordinate query schemas if direct lat/lon endpoints are added.
"""

from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class WeatherUnits(StrEnum):
    """Supported Weather unit systems."""

    METRIC = "metric"
    IMPERIAL = "imperial"


class CityQuery(BaseModel):
    """Reusable Weather city query."""

    city: str = Field(..., min_length=1, max_length=120, examples=["Kolkata"])
    country: str | None = Field(None, min_length=2, max_length=80, examples=["IN"])

    @field_validator("city", "country")
    @classmethod
    def no_blank(cls, value: str | None) -> str | None:
        """Reject blank city or country values."""
        if value is not None and not value.strip():
            raise ValueError("value cannot be blank")
        return value.strip() if value else value
