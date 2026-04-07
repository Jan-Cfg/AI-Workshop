"""
Unit Tests for Security Components
Tests authentication, encryption, and input validation.
"""
import pytest
from src.security.auth import Auth
from src.security.encryption import EncryptionManager
from src.utils.helpers import sanitize_input, validate_query


class TestAuth:
    """Authentication tests."""

    def test_token_generation(self):
        """Test API token generation."""
        auth = Auth(secret_key="test_secret")
        token = auth.generate_token(user_id="user123", scopes=["read", "write"])

        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_validation(self):
        """Test token validation."""
        auth = Auth(secret_key="test_secret")
        token = auth.generate_token(user_id="user123")

        assert auth.validate_token(token) is True
        assert auth.validate_token("invalid_token") is False

    def test_scope_validation(self):
        """Test scope validation."""
        auth = Auth(secret_key="test_secret")
        token = auth.generate_token(user_id="user123", scopes=["read"])

        assert auth.validate_token(token, required_scope="read") is True
        assert auth.validate_token(token, required_scope="write") is False

    def test_user_extraction(self):
        """Test extracting user from token."""
        auth = Auth(secret_key="test_secret")
        token = auth.generate_token(user_id="user123")

        user_id = auth.get_user_from_token(token)
        assert user_id == "user123"

    def test_invalid_token_extraction(self):
        """Test extracting user from invalid token."""
        auth = Auth(secret_key="test_secret")
        user_id = auth.get_user_from_token("invalid_token")
        assert user_id is None

    def test_token_revocation(self):
        """Test token revocation."""
        auth = Auth(secret_key="test_secret")
        token = auth.generate_token(user_id="user123")

        assert auth.revoke_token(token) is True
        assert auth.validate_token(token) is False

    def test_password_hashing(self):
        """Test secure password hashing."""
        password = "my_secure_password"
        hashed, salt = Auth.hash_password(password)

        assert isinstance(hashed, str)
        assert isinstance(salt, str)
        assert len(hashed) > 0
        assert len(salt) > 0

    def test_password_verification(self):
        """Test password verification."""
        password = "my_secure_password"
        hashed, salt = Auth.hash_password(password)

        assert Auth.verify_password(password, hashed, salt) is True
        assert Auth.verify_password("wrong_password", hashed, salt) is False


class TestEncryption:
    """Encryption tests."""

    def test_key_generation(self):
        """Test encryption key generation."""
        key = EncryptionManager.generate_key()

        assert isinstance(key, bytes)
        assert len(key) > 0

    def test_data_encryption_decryption(self):
        """Test data encryption and decryption."""
        key = EncryptionManager.generate_key()
        plaintext = "sensitive_data"

        encrypted = EncryptionManager.encrypt_data(plaintext, key)
        decrypted = EncryptionManager.decrypt_data(encrypted, key)

        assert encrypted != plaintext
        assert decrypted == plaintext

    def test_key_derivation_from_password(self):
        """Test deriving encryption key from password."""
        password = "user_password"
        key, salt = EncryptionManager.derive_key_from_password(password)

        assert isinstance(key, bytes)
        assert isinstance(salt, bytes)
        assert len(key) > 0

    def test_consistent_key_derivation(self):
        """Test that same password produces same key."""
        password = "user_password"
        salt = b"fixed_salt_16byt"

        key1, _ = EncryptionManager.derive_key_from_password(password, salt)
        key2, _ = EncryptionManager.derive_key_from_password(password, salt)

        assert key1 == key2

    def test_data_hashing(self):
        """Test data hashing."""
        data = "test_data"
        hash1 = EncryptionManager.hash_data(data)
        hash2 = EncryptionManager.hash_data(data)

        assert isinstance(hash1, str)
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex length


class TestInputValidation:
    """Input validation and sanitization tests."""

    def test_query_validation(self):
        """Test query validation."""
        valid_query = "What is machine learning?"
        assert validate_query(valid_query) == valid_query

        with pytest.raises(ValueError):
            validate_query("")

        with pytest.raises(ValueError):
            validate_query("ab")  # Too short

    def test_input_sanitization(self):
        """Test input sanitization preventing injection."""
        malicious_input = "hello<script>alert('xss')</script>"
        sanitized = sanitize_input(malicious_input)

        assert "<script>" not in sanitized
        assert "alert" in sanitized  # Content preserved, tags removed

    def test_sanitization_preserves_safe_content(self):
        """Test that sanitization preserves safe input."""
        safe_input = "What is artificial intelligence?"
        sanitized = sanitize_input(safe_input)

        assert sanitized == safe_input


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
    unittest.main()