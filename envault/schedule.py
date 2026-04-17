"""Schedule-based auto-push reminders for envault."""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


class ScheduleError(Exception):
    pass


def _schedule_path(config_dir: Path) -> Path:
    return config_dir / ".envault_schedule.json"


def save_schedule(config_dir: Path, interval_days: int) -> None:
    if interval_days < 1:
        raise ScheduleError("interval_days must be >= 1")
    data = {"interval_days": interval_days, "created_at": datetime.utcnow().isoformat()}
    _schedule_path(config_dir).write_text(json.dumps(data))


def load_schedule(config_dir: Path) -> Optional[dict]:
    p = _schedule_path(config_dir)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError as e:
        raise ScheduleError(f"Corrupt schedule file: {e}") from e


def delete_schedule(config_dir: Path) -> None:
    p = _schedule_path(config_dir)
    if not p.exists():
        raise ScheduleError("No schedule configured.")
    p.unlink()


def check_schedule_due(config_dir: Path, last_push_iso: Optional[str]) -> bool:
    """Return True if a push is due based on the saved schedule."""
    schedule = load_schedule(config_dir)
    if schedule is None:
        return False
    if last_push_iso is None:
        return True
    last = datetime.fromisoformat(last_push_iso)
    due = last + timedelta(days=schedule["interval_days"])
    return datetime.utcnow() >= due
