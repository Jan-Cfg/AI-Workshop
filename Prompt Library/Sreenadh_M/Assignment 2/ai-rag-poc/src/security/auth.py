"""
Authentication and Authorization Security Module
Demonstrates secure authentication mechanisms for AI products.
"""
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any


class Auth:
    """Authentication handler with token management."""

    def __init__(self, secret_key: str, token_expiry_hours: int = 24):
        self.secret_key = secret_key
        self.token_expiry_hours = token_expiry_hours
        self.valid_tokens: Dict[str, Dict[str, Any]] = {}  # In-memory token store (use Redis in production)

    def generate_token(self, user_id: str, scopes: list[str] = None) -> str:
        """
        Generate secure API token for user.

        Args:
            user_id: Unique user identifier
            scopes: List of permissions (e.g., ["read", "write"])

        Returns:
            Secure token string
        """
        scopes = scopes or ["read"]
        token = secrets.token_urlsafe(32)

        # Store token metadata
        self.valid_tokens[token] = {
            "user_id": user_id,
            "scopes": scopes,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(hours=self.token_expiry_hours),
        }

        return token

    def validate_token(self, token: str, required_scope: str = "read") -> bool:
        """
        Validate user token and check expiry.

        Args:
            token: API token
            required_scope: Required permission scope

        Returns:
            True if valid, False otherwise
        """
        if token not in self.valid_tokens:
            return False

        token_data = self.valid_tokens[token]

        # Check expiry
        if datetime.now() > token_data["expires_at"]:
            del self.valid_tokens[token]
            return False

        # Check scope
        if required_scope and required_scope not in token_data["scopes"]:
            return False

        return True

    def get_user_from_token(self, token: str) -> Optional[str]:
        """Extract user ID from valid token."""
        if self.validate_token(token):
            return self.valid_tokens[token]["user_id"]
        return None

    def revoke_token(self, token: str) -> bool:
        """Revoke a token."""
        if token in self.valid_tokens:
            del self.valid_tokens[token]
            return True
        return False

    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """
        Hash password securely using PBKDF2.

        Args:
            password: Plain text password
            salt: Optional salt (generated if not provided)

        Returns:
            (hashed_password, salt) tuple
        """
        if not salt:
            salt = secrets.token_hex(16)

        pwd_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            salt.encode(),
            100000,  # iterations
        )

        return pwd_hash.hex(), salt

    @staticmethod
    def verify_password(password: str, stored_hash: str, salt: str) -> bool:
        """Verify password against stored hash."""
        pwd_hash, _ = Auth.hash_password(password, salt)
        return hmac.compare_digest(pwd_hash, stored_hash)
