"""Shared type definitions.

Purpose: provide reusable aliases for infrastructure code.
Responsibilities: improve readability without introducing runtime behavior.
Dependencies: standard library typing.
Extension Notes: prefer domain-specific types near their bounded context.
"""

from collections.abc import Mapping

JsonPrimitive = str | int | float | bool | None
JsonValue = JsonPrimitive | list["JsonValue"] | Mapping[str, "JsonValue"]
JsonObject = Mapping[str, JsonValue]

