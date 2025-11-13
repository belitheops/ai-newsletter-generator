import hashlib
import secrets
import json
from typing import Optional, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthManager:
    """Manages user authentication with secure password hashing"""

    def __init__(self):
        self.salt_length = 32

    def _generate_salt(self) -> str:
        """Generate a random salt for password hashing"""
        return secrets.token_hex(self.salt_length)

    def _hash_password(self, password: str, salt: str) -> str:
        """Hash a password with a salt using SHA-256"""
        password_salt = (password + salt).encode('utf-8')
        return hashlib.sha256(password_salt).hexdigest()

    def create_password_hash(self, password: str) -> Dict[str, str]:
        """Create a salted hash for a new password"""
        salt = self._generate_salt()
        password_hash = self._hash_password(password, salt)
        return {
            'salt': salt,
            'hash': password_hash
        }

    def verify_password(self, password: str, salt: str, stored_hash: str) -> bool:
        """Verify a password against a stored hash"""
        password_hash = self._hash_password(password, salt)
        return password_hash == stored_hash

    def validate_password_strength(self, password: str) -> tuple[bool, str]:
        """
        Validate password meets security requirements
        Returns (is_valid, error_message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"

        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)

        if not (has_upper and has_lower and has_digit):
            return False, "Password must contain at least one uppercase letter, one lowercase letter, and one digit"

        return True, ""

    def validate_username(self, username: str) -> tuple[bool, str]:
        """
        Validate username meets requirements
        Returns (is_valid, error_message)
        """
        if len(username) < 3:
            return False, "Username must be at least 3 characters long"

        if len(username) > 30:
            return False, "Username must be at most 30 characters long"

        if not username.replace('_', '').replace('-', '').isalnum():
            return False, "Username can only contain letters, numbers, hyphens, and underscores"

        return True, ""

    def validate_email(self, email: str) -> tuple[bool, str]:
        """
        Basic email validation
        Returns (is_valid, error_message)
        """
        if '@' not in email or '.' not in email.split('@')[-1]:
            return False, "Please enter a valid email address"

        if len(email) < 5:
            return False, "Email address is too short"

        return True, ""
