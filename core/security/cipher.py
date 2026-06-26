"""Token encryption service.

Purpose: encrypt and decrypt OAuth tokens before persistence.
Responsibilities: wrap Fernet with configuration validation.
Dependencies: cryptography and application exceptions.
Extension Notes: support key ids and rotation before multi-tenant scale.
"""

from cryptography.fernet import Fernet, InvalidToken
from pydantic import SecretStr

from core.exceptions import ConfigurationException, ValidationException


class TokenCipher:
    """Encrypts and decrypts sensitive token values."""

    def __init__(self, key: SecretStr | None) -> None:
        """Create a cipher from a configured Fernet key."""
        if key is None:
            raise ConfigurationException(
                message="OAuth token encryption key is required",
                code="security.encryption_key_missing",
            )
        self._fernet = Fernet(key.get_secret_value().encode())

    def encrypt(self, value: str) -> str:
        """Encrypt a plaintext token."""
        return self._fernet.encrypt(value.encode()).decode()

    def decrypt(self, value: str) -> str:
        """Decrypt a stored token."""
        try:
            return self._fernet.decrypt(value.encode()).decode()
        except InvalidToken as exc:
            raise ValidationException(
                message="Encrypted token could not be decrypted",
                code="security.invalid_token_ciphertext",
            ) from exc

