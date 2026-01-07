"""
Authentication Service for HR Admin

Security features:
- Constant-time password comparison (prevent timing attacks)
- No plaintext password storage in session
- Session-based authentication state
- File-based session persistence
"""
import hashlib
import hmac
import json
import os
import secrets
import time
from pathlib import Path
from typing import Optional

from config.settings import Settings

# Session configuration (use Settings value)
SESSION_FILE = Path(Settings.BASE_DIR) / "data" / ".sessions.json"


class AuthService:
    """
    Simple authentication service for HR admin access.

    Security considerations:
    - Uses hmac.compare_digest for constant-time comparison
    - Generates session tokens instead of storing passwords
    - No SQL/NoSQL database = no injection vulnerabilities
    - File-based session persistence with expiry
    """

    def __init__(self):
        self._session_tokens: dict[str, dict] = {}
        self._load_sessions()

    def _load_sessions(self) -> None:
        """Load sessions from file"""
        try:
            if SESSION_FILE.exists():
                with open(SESSION_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Filter expired sessions
                    now = time.time()
                    self._session_tokens = {
                        token: info for token, info in data.items()
                        if info.get("expires_at", 0) > now
                    }
                    # Save back without expired sessions
                    if len(self._session_tokens) != len(data):
                        self._save_sessions()
        except (json.JSONDecodeError, IOError):
            self._session_tokens = {}

    def _save_sessions(self) -> None:
        """Save sessions to file"""
        try:
            SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(SESSION_FILE, "w", encoding="utf-8") as f:
                json.dump(self._session_tokens, f)
        except IOError:
            pass

    def _hash_password(self, password: str) -> str:
        """
        Hash password for comparison.
        Using SHA-256 for simple hashing (passwords are from env, not user-created)
        """
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def verify_credentials(self, username: str, password: str) -> bool:
        """
        Verify username and password against configured credentials.

        Uses constant-time comparison to prevent timing attacks.

        Args:
            username: Provided username
            password: Provided password

        Returns:
            True if credentials are valid
        """
        # Check if HR credentials are configured
        if not Settings.HR_PASSWORD:
            # No password set = authentication disabled (development mode)
            return False

        # Sanitize inputs (prevent any injection-like attacks)
        username = str(username).strip()
        password = str(password)

        # Constant-time comparison for both username and password
        # This prevents timing attacks that could reveal valid usernames
        username_valid = hmac.compare_digest(
            username.encode('utf-8'),
            Settings.HR_USERNAME.encode('utf-8')
        )

        password_valid = hmac.compare_digest(
            self._hash_password(password),
            self._hash_password(Settings.HR_PASSWORD)
        )

        return username_valid and password_valid

    def create_session_token(self, username: str) -> str:
        """
        Create a secure session token for authenticated user.

        Args:
            username: Authenticated username

        Returns:
            Secure random token
        """
        token = secrets.token_urlsafe(32)
        expires_at = time.time() + (Settings.SESSION_EXPIRY_HOURS * 3600)
        self._session_tokens[token] = {
            "username": username,
            "created_at": time.time(),
            "expires_at": expires_at
        }
        self._save_sessions()
        return token

    def validate_session_token(self, token: str) -> Optional[str]:
        """
        Validate a session token.

        Args:
            token: Session token to validate

        Returns:
            Username if valid, None otherwise
        """
        if not token:
            return None

        session = self._session_tokens.get(token)
        if not session:
            return None

        # Check expiry
        if session.get("expires_at", 0) < time.time():
            self.invalidate_session(token)
            return None

        return session.get("username")

    def invalidate_session(self, token: str) -> bool:
        """
        Invalidate (logout) a session.

        Args:
            token: Session token to invalidate

        Returns:
            True if session was invalidated
        """
        if token in self._session_tokens:
            del self._session_tokens[token]
            self._save_sessions()
            return True
        return False

    def is_auth_enabled(self) -> bool:
        """
        Check if authentication is enabled.

        Returns:
            True if HR_PASSWORD is configured
        """
        return bool(Settings.HR_PASSWORD)


# Singleton instance
auth_service = AuthService()


def verify_login(username: str, password: str) -> Optional[str]:
    """
    Convenience function to verify login and create session.

    Args:
        username: Username
        password: Password

    Returns:
        Session token if successful, None otherwise
    """
    if auth_service.verify_credentials(username, password):
        return auth_service.create_session_token(username)
    return None


def check_session(token: str) -> bool:
    """
    Convenience function to check if session is valid.

    Args:
        token: Session token

    Returns:
        True if session is valid
    """
    return auth_service.validate_session_token(token) is not None


def logout(token: str) -> bool:
    """
    Convenience function to logout.

    Args:
        token: Session token

    Returns:
        True if logout successful
    """
    return auth_service.invalidate_session(token)


def is_auth_required() -> bool:
    """
    Check if authentication is required.

    Returns:
        True if HR_PASSWORD is set in environment
    """
    return auth_service.is_auth_enabled()
