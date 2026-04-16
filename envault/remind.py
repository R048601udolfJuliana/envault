"""Rotation reminder — warns when encrypted file hasn't been rotated recently."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional

REMIND_FILE = ".envault_remind.json"
DEFAULT_MAX_AGE_DAYS = 30


class RemindError(Exception):
    pass


def _remind_path(config_dir: Path) -> Path:
    return config_dir / REMIND_FILE


def record_rotation(config_dir: Path) -> None:
    """Record the current timestamp as the last rotation time."""
    path = _remind_path(config_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {"last_rotated": time.time()}
    path.write_text(json.dumps(data))


def load_last_rotation(config_dir: Path) -> Optional[float]:
    """Return the last rotation timestamp or None if never recorded."""
    path = _remind_path(config_dir)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        return float(data["last_rotated"])
    except (KeyError, ValueError, json.JSONDecodeError) as exc:
        raise RemindError(f"Corrupt remind file: {exc}") from exc


def check_rotation_due(config_dir: Path, max_age_days: int = DEFAULT_MAX_AGE_DAYS) -> bool:
    """Return True if rotation is overdue or has never been recorded."""
    last = load_last_rotation(config_dir)
    if last is None:
        return True
    age_days = (time.time() - last) / 86400
    return age_days >= max_age_days


def days_since_rotation(config_dir: Path) -> Optional[float]:
    """Return number of days since last rotation, or None if never."""
    last = load_last_rotation(config_dir)
    if last is None:
        return None
    return (time.time() - last) / 86400
