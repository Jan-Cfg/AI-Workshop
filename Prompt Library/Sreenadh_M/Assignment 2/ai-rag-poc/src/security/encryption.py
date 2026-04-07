"""
Data Encryption and Protection Module
Demonstrates encryption mechanisms for securing AI product data.
"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64
import secrets
import os


class EncryptionManager:
    """Handles encryption/decryption of sensitive data."""

    @staticmethod
    def generate_key() -> bytes:
        """Generate a new Fernet encryption key."""
        return Fernet.generate_key()

    @staticmethod
    def encrypt_data(data: str, key: bytes) -> str:
        """
        Encrypt plain text using Fernet symmetric encryption.

        Args:
            data: Plain text to encrypt
            key: Encryption key (from generate_key or derive_key)

        Returns:
            Base64-encoded encrypted data
        """
        cipher = Fernet(key)
        encrypted = cipher.encrypt(data.encode())
        return base64.b64encode(encrypted).decode()

    @staticmethod
    def decrypt_data(encrypted_data: str, key: bytes) -> str:
        """
        Decrypt Fernet-encrypted data.

        Args:
            encrypted_data: Base64-encoded encrypted data
            key: Encryption key

        Returns:
            Decrypted plain text
        """
        cipher = Fernet(key)
        encrypted = base64.b64decode(encrypted_data.encode())
        decrypted = cipher.decrypt(encrypted)
        return decrypted.decode()

    @staticmethod
    def derive_key_from_password(password: str, salt: bytes = None) -> tuple[bytes, bytes]:
        """
        Derive encryption key from password using PBKDF2.

        Useful for protecting user-specific data.

        Args:
            password: User password
            salt: Optional salt (generated if not provided)

        Returns:
            (encryption_key, salt) tuple
        """
        if not salt:
            salt = secrets.token_bytes(16)

        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt

    @staticmethod
    def hash_data(data: str) -> str:
        """Hash data using SHA-256 for verification."""
        from hashlib import sha256
        return sha256(data.encode()).hexdigest()
