"""TTL (time-to-live) enforcement for encrypted .env files."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional

TTL_FILENAME = ".envault_ttl"


class TTLError(Exception):
    """Raised when a TTL operation fails."""


def _ttl_path(directory: Path) -> Path:
    return directory / TTL_FILENAME


def set_ttl(directory: Path, seconds: int) -> None:
    """Record a TTL (in seconds) starting from now."""
    if seconds <= 0:
        raise TTLError("TTL must be a positive integer number of seconds.")
    data = {"created_at": time.time(), "ttl_seconds": seconds}
    _ttl_path(directory).write_text(json.dumps(data))


def load_ttl(directory: Path) -> Optional[dict]:
    """Load TTL metadata, or return None if not set."""
    path = _ttl_path(directory)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, KeyError) as exc:
        raise TTLError(f"Corrupt TTL file: {exc}") from exc


def is_expired(directory: Path) -> bool:
    """Return True if the TTL has elapsed, False if still valid or not set."""
    data = load_ttl(directory)
    if data is None:
        return False
    elapsed = time.time() - data["created_at"]
    return elapsed > data["ttl_seconds"]


def remaining_seconds(directory: Path) -> Optional[float]:
    """Return seconds remaining, 0 if expired, or None if no TTL is set."""
    data = load_ttl(directory)
    if data is None:
        return None
    remaining = data["ttl_seconds"] - (time.time() - data["created_at"])
    return max(0.0, remaining)


def clear_ttl(directory: Path) -> None:
    """Remove the TTL file if it exists."""
    path = _ttl_path(directory)
    if path.exists():
        path.unlink()
