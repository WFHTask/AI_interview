"""
Rate Limiter Utility

Simple in-memory rate limiting for API and interview requests.
Uses sliding window algorithm for accurate rate limiting.
"""
import time
import threading
from collections import defaultdict
from typing import Optional


class RateLimiter:
    """
    Thread-safe rate limiter using sliding window algorithm.

    IMPORTANT: This is an in-memory rate limiter. In multi-process deployments
    (e.g., Gunicorn with multiple workers), each process maintains its own
    rate limit state. The effective rate limit becomes:
        actual_limit = configured_limit × number_of_workers

    For strict rate limiting in multi-process environments, consider using
    Redis-based rate limiting instead.

    Usage:
        limiter = RateLimiter(max_requests=10, window_seconds=60)
        if limiter.is_allowed("user_123"):
            # Process request
        else:
            # Rate limited
    """

    def __init__(
        self,
        max_requests: int = 10,
        window_seconds: float = 60.0,
        cleanup_interval: float = 300.0
    ):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
            cleanup_interval: How often to cleanup old entries (seconds)
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.cleanup_interval = cleanup_interval

        self._requests: dict[str, list[float]] = defaultdict(list)
        self._lock = threading.Lock()
        self._last_cleanup = time.time()

    def is_allowed(self, key: str) -> bool:
        """
        Check if request is allowed for given key.

        Args:
            key: Identifier (IP, user ID, session ID, etc.)

        Returns:
            True if request is allowed
        """
        current_time = time.time()

        with self._lock:
            # Periodic cleanup
            if current_time - self._last_cleanup > self.cleanup_interval:
                self._cleanup(current_time)

            # Get request timestamps for this key
            timestamps = self._requests[key]

            # Filter timestamps within window
            window_start = current_time - self.window_seconds
            valid_timestamps = [ts for ts in timestamps if ts > window_start]

            # Update timestamps
            self._requests[key] = valid_timestamps

            # Check if under limit
            if len(valid_timestamps) < self.max_requests:
                self._requests[key].append(current_time)
                return True

            return False

    def get_remaining(self, key: str) -> int:
        """
        Get remaining requests for key.

        Args:
            key: Identifier

        Returns:
            Number of remaining requests allowed
        """
        current_time = time.time()
        window_start = current_time - self.window_seconds

        with self._lock:
            timestamps = self._requests.get(key, [])
            valid_count = sum(1 for ts in timestamps if ts > window_start)
            return max(0, self.max_requests - valid_count)

    def get_reset_time(self, key: str) -> Optional[float]:
        """
        Get time until rate limit resets.

        Args:
            key: Identifier

        Returns:
            Seconds until reset, or None if not rate limited
        """
        current_time = time.time()
        window_start = current_time - self.window_seconds

        with self._lock:
            timestamps = self._requests.get(key, [])
            valid_timestamps = [ts for ts in timestamps if ts > window_start]

            if len(valid_timestamps) >= self.max_requests:
                oldest = min(valid_timestamps)
                return (oldest + self.window_seconds) - current_time

            return None

    def reset(self, key: str) -> None:
        """
        Reset rate limit for a key.

        Args:
            key: Identifier to reset
        """
        with self._lock:
            if key in self._requests:
                del self._requests[key]

    def _cleanup(self, current_time: float) -> None:
        """Remove old entries to prevent memory growth"""
        window_start = current_time - self.window_seconds

        keys_to_remove = []
        for key, timestamps in self._requests.items():
            # Keep only recent timestamps
            self._requests[key] = [ts for ts in timestamps if ts > window_start]

            # Mark empty entries for removal
            if not self._requests[key]:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self._requests[key]

        self._last_cleanup = current_time


class InterviewRateLimiter:
    """
    Specialized rate limiter for interview requests.

    Limits:
    - Per-session: Prevents rapid-fire messages
    - Per-IP: Prevents abuse from single source
    - Global: Prevents system overload
    """

    def __init__(self):
        # Import settings for configurable limits
        from config.settings import Settings

        # Per-session: 5 messages per 10 seconds
        self.session_limiter = RateLimiter(max_requests=5, window_seconds=10)

        # Per-IP: configurable requests per minute
        self.ip_limiter = RateLimiter(
            max_requests=Settings.RATE_LIMIT_REQUESTS,
            window_seconds=Settings.RATE_LIMIT_WINDOW
        )

        # Global: 100 requests per minute (for small deployment)
        self.global_limiter = RateLimiter(max_requests=100, window_seconds=60)

    def check_request(
        self,
        session_id: str,
        ip_address: Optional[str] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Check if interview request is allowed.

        Args:
            session_id: Interview session ID
            ip_address: Client IP address (optional)

        Returns:
            Tuple of (is_allowed, error_message)
        """
        # Check global limit first
        if not self.global_limiter.is_allowed("global"):
            return False, "系统繁忙，请稍后再试"

        # Check IP limit
        if ip_address and not self.ip_limiter.is_allowed(ip_address):
            reset_time = self.ip_limiter.get_reset_time(ip_address)
            wait_seconds = int(reset_time) if reset_time else 60
            return False, f"请求过于频繁，请等待 {wait_seconds} 秒后重试"

        # Check session limit
        if not self.session_limiter.is_allowed(session_id):
            reset_time = self.session_limiter.get_reset_time(session_id)
            wait_seconds = int(reset_time) if reset_time else 10
            return False, f"消息发送过快，请等待 {wait_seconds} 秒"

        return True, None


# Singleton instance
interview_rate_limiter = InterviewRateLimiter()


def check_interview_rate_limit(
    session_id: str,
    ip_address: Optional[str] = None
) -> tuple[bool, Optional[str]]:
    """
    Convenience function to check interview rate limit.

    Args:
        session_id: Interview session ID
        ip_address: Client IP (optional)

    Returns:
        Tuple of (is_allowed, error_message)
    """
    return interview_rate_limiter.check_request(session_id, ip_address)
