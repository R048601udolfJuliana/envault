"""Watch .env file for changes and auto-push on modification."""

import time
import os
from pathlib import Path
from typing import Callable, Optional


class WatchError(Exception):
    """Raised when watching fails."""


def _mtime(path: Path) -> float:
    """Return modification time of a file, or 0.0 if missing."""
    try:
        return path.stat().st_mtime
    except FileNotFoundError:
        return 0.0


def watch(
    env_path: Path,
    on_change: Callable[[Path], None],
    interval: float = 1.0,
    max_iterations: Optional[int] = None,
) -> None:
    """Poll *env_path* every *interval* seconds and call *on_change* when it changes.

    Args:
        env_path: Path to the .env file to watch.
        on_change: Callback invoked with the path whenever a change is detected.
        interval: Polling interval in seconds.
        max_iterations: Stop after this many poll cycles (useful for testing).

    Raises:
        WatchError: If *env_path* does not exist at startup.
    """
    if not env_path.exists():
        raise WatchError(f"File not found: {env_path}")

    last_mtime = _mtime(env_path)
    iterations = 0

    while True:
        time.sleep(interval)
        current_mtime = _mtime(env_path)

        if current_mtime != last_mtime:
            last_mtime = current_mtime
            on_change(env_path)

        iterations += 1
        if max_iterations is not None and iterations >= max_iterations:
            break
