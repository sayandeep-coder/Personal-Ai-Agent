"""Configuration package.

Purpose: expose the singleton settings object.
Responsibilities: load validated environment configuration once.
Dependencies: Pydantic Settings.
Extension Notes: split nested settings when configuration grows.
"""

from core.config.settings import Settings, get_settings, settings

__all__ = ["Settings", "get_settings", "settings"]

