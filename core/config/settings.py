"""Application settings.

Purpose: load environment variables into a validated settings object.
Responsibilities: define configuration schema and singleton access.
Dependencies: Pydantic Settings and core constants.
Extension Notes: add grouped nested settings as the platform grows.
"""

from functools import lru_cache
from typing import Self

from pydantic import SecretStr, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.config.enums import AppEnvironment, LogLevel
from core.config.validators import validate_iana_timezone, validate_required_url
from core.constants import DEFAULT_APP_NAME, DEFAULT_TIMEZONE


class Settings(BaseSettings):
    """Validated process configuration loaded from environment variables."""

    app_name: str = DEFAULT_APP_NAME
    app_env: AppEnvironment = AppEnvironment.DEVELOPMENT
    debug: bool = False
    timezone: str = DEFAULT_TIMEZONE
    log_level: LogLevel = LogLevel.INFO
    database_url: str
    redis_url: str
    openai_api_key: SecretStr | None = None
    openai_model: str = "gpt-5"
    google_client_id: str | None = None
    google_client_secret: SecretStr | None = None
    google_maps_api_key: SecretStr | None = None
    github_token: SecretStr | None = None
    weather_api_key: SecretStr | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @field_validator("*", mode="before")
    @classmethod
    def empty_string_to_none(cls, value: object) -> object:
        """Normalize blank secret or optional environment values."""
        return None if value == "" else value

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, value: object) -> object:
        """Parse common boolean and deployment-style debug values."""
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"true", "1", "yes", "on", "debug", "development"}:
                return True
            if normalized in {"false", "0", "no", "off", "release", "production"}:
                return False
        return value

    @field_validator("database_url", "redis_url")
    @classmethod
    def required_urls(cls, value: str, info: ValidationInfo) -> str:
        """Validate required infrastructure URLs."""
        return validate_required_url(value, info.field_name or "url")

    @field_validator("timezone")
    @classmethod
    def valid_timezone(cls, value: str) -> str:
        """Validate the configured IANA timezone."""
        return validate_iana_timezone(value)

    @property
    def is_production(self: Self) -> bool:
        """Return whether the process is running in production."""
        return self.app_env == AppEnvironment.PRODUCTION

    def safe_dict(self: Self) -> dict[str, str | bool]:
        """Return non-sensitive configuration values."""
        return {
            "app_name": self.app_name,
            "app_env": self.app_env.value,
            "debug": self.debug,
            "timezone": self.timezone,
            "log_level": self.log_level.value,
            "openai_model": self.openai_model,
        }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the singleton settings object for this process."""
    return Settings()


settings = get_settings()
