"""
File Locking Utility

Simple cross-platform file locking for preventing concurrent writes.
Uses fcntl on Unix and msvcrt on Windows.
"""
import os
import time
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

# Thread-level locks for same-process coordination
_thread_locks: dict[str, threading.Lock] = {}
_thread_locks_lock = threading.Lock()


def _get_thread_lock(path: str) -> threading.Lock:
    """Get or create thread lock for a path"""
    with _thread_locks_lock:
        if path not in _thread_locks:
            _thread_locks[path] = threading.Lock()
        return _thread_locks[path]


class FileLock:
    """
    Cross-platform file lock with timeout support.

    Uses a .lock file alongside the target file.
    Implements both thread-level and process-level locking.
    """

    def __init__(self, path: str, timeout: float = 10.0):
        """
        Initialize file lock.

        Args:
            path: Path to the file to lock
            timeout: Maximum time to wait for lock (seconds)
        """
        self.path = str(path)
        self.lock_path = f"{self.path}.lock"
        self.timeout = timeout
        self.lock_file = None
        self._thread_lock = _get_thread_lock(self.path)

    def acquire(self) -> bool:
        """
        Acquire the lock.

        Returns:
            True if lock acquired, False if timeout
        """
        start_time = time.time()

        # First acquire thread lock
        if not self._thread_lock.acquire(timeout=self.timeout):
            return False

        remaining_timeout = self.timeout - (time.time() - start_time)
        if remaining_timeout <= 0:
            self._thread_lock.release()
            return False

        # Then acquire file lock
        try:
            while time.time() - start_time < self.timeout:
                try:
                    # Try to create lock file exclusively
                    self.lock_file = os.open(
                        self.lock_path,
                        os.O_CREAT | os.O_EXCL | os.O_WRONLY
                    )
                    # Write PID for debugging
                    os.write(self.lock_file, str(os.getpid()).encode())
                    return True
                except FileExistsError:
                    # Lock file exists, check if stale
                    if self._is_stale_lock():
                        self._remove_stale_lock()
                        continue
                    # Wait and retry
                    time.sleep(0.1)
                except OSError:
                    time.sleep(0.1)

            # Timeout reached
            self._thread_lock.release()
            return False

        except Exception:
            self._thread_lock.release()
            raise

    def release(self) -> None:
        """Release the lock"""
        try:
            if self.lock_file is not None:
                os.close(self.lock_file)
                self.lock_file = None

            # Remove lock file
            if os.path.exists(self.lock_path):
                os.remove(self.lock_path)
        except OSError:
            pass  # Ignore errors during cleanup
        finally:
            try:
                self._thread_lock.release()
            except RuntimeError:
                pass  # Already released

    def _is_stale_lock(self, max_age: float = 60.0) -> bool:
        """
        Check if lock file is stale (older than max_age seconds).

        Args:
            max_age: Maximum age in seconds before considering stale

        Returns:
            True if lock is stale
        """
        try:
            if not os.path.exists(self.lock_path):
                return False

            mtime = os.path.getmtime(self.lock_path)
            age = time.time() - mtime
            return age > max_age
        except OSError:
            return True  # Assume stale if can't check

    def _remove_stale_lock(self) -> None:
        """Remove stale lock file"""
        try:
            os.remove(self.lock_path)
        except OSError:
            pass

    def __enter__(self):
        """Context manager entry"""
        if not self.acquire():
            raise TimeoutError(f"Could not acquire lock for {self.path}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.release()
        return False


@contextmanager
def file_lock(path: str, timeout: float = 10.0):
    """
    Context manager for file locking.

    Usage:
        with file_lock("/path/to/file.json"):
            # Read/write file safely
            pass

    Args:
        path: Path to file
        timeout: Lock timeout in seconds

    Raises:
        TimeoutError: If lock cannot be acquired
    """
    lock = FileLock(path, timeout)
    if not lock.acquire():
        raise TimeoutError(f"Could not acquire lock for {path} within {timeout}s")
    try:
        yield lock
    finally:
        lock.release()


def safe_write_json(path: str, data: dict, timeout: float = 10.0) -> None:
    """
    Safely write JSON data to file with locking.

    Uses atomic write (write to temp file, then rename).

    Args:
        path: Target file path
        data: Data to write
        timeout: Lock timeout

    Raises:
        TimeoutError: If lock cannot be acquired
    """
    import json
    import tempfile

    path = str(path)
    dir_path = os.path.dirname(path) or "."

    with file_lock(path, timeout):
        # Write to temp file first
        fd, temp_path = tempfile.mkstemp(
            suffix=".tmp",
            dir=dir_path
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)

            # Atomic rename (works on same filesystem)
            if os.path.exists(path):
                os.replace(temp_path, path)
            else:
                os.rename(temp_path, path)
        except Exception:
            # Cleanup temp file on error
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise


def safe_read_json(path: str, timeout: float = 10.0, default: Optional[dict] = None) -> Optional[dict]:
    """
    Safely read JSON data from file with locking.

    Args:
        path: File path
        timeout: Lock timeout
        default: Default value if file doesn't exist

    Returns:
        Parsed JSON data or default

    Raises:
        TimeoutError: If lock cannot be acquired
    """
    import json

    path = str(path)

    if not os.path.exists(path):
        return default

    with file_lock(path, timeout):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return default
