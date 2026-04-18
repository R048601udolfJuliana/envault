"""envault.lock — file-based lock to prevent concurrent vault operations."""
from __future__ import annotations

import os
import time
from pathlib import Path


class LockError(Exception):
    """Raised when a lock cannot be acquired or released."""


_LOCK_FILENAME = ".envault.lock"


def _lock_path(config_dir: Path) -> Path:
    return config_dir / _LOCK_FILENAME


def acquire(config_dir: Path, timeout: float = 10.0, poll: float = 0.2) -> Path:
    """Acquire a lock file, waiting up to *timeout* seconds.

    Returns the path to the lock file on success.
    Raises LockError if the lock cannot be acquired within the timeout.
    """
    lock = _lock_path(config_dir)
    deadline = time.monotonic() + timeout
    while True:
        try:
            fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            return lock
        except FileExistsError:
            if time.monotonic() >= deadline:
                owner = _read_owner(lock)
                raise LockError(
                    f"Could not acquire lock {lock} (held by pid {owner}). "
                    "Another envault process may be running."
                )
            time.sleep(poll)


def release(lock: Path) -> None:
    """Release (delete) the lock file."""
    try:
        lock.unlink()
    except FileNotFoundError:
        raise LockError(f"Lock file {lock} not found; it may have been removed externally.")


def is_locked(config_dir: Path) -> bool:
    """Return True if a lock file currently exists."""
    return _lock_path(config_dir).exists()


def _read_owner(lock: Path) -> str:
    try:
        return lock.read_text().strip()
    except OSError:
        return "unknown"
