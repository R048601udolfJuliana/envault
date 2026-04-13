"""Track a local history of push/pull operations for auditing and rollback reference."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


class HistoryError(Exception):
    """Raised when history operations fail."""


_HISTORY_FILE = ".envault_history.json"
_MAX_ENTRIES = 100


@dataclass
class HistoryEntry:
    action: str  # "push" or "pull"
    timestamp: float
    encrypted_file: str
    recipients: List[str] = field(default_factory=list)
    note: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "action": self.action,
            "timestamp": self.timestamp,
            "encrypted_file": self.encrypted_file,
            "recipients": self.recipients,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "HistoryEntry":
        return cls(
            action=data["action"],
            timestamp=data["timestamp"],
            encrypted_file=data["encrypted_file"],
            recipients=data.get("recipients", []),
            note=data.get("note"),
        )

    def human_time(self) -> str:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.timestamp))


def _history_path(base_dir: Path) -> Path:
    return base_dir / _HISTORY_FILE


def load_history(base_dir: Path) -> List[HistoryEntry]:
    path = _history_path(base_dir)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return [HistoryEntry.from_dict(e) for e in data]
    except (json.JSONDecodeError, KeyError) as exc:
        raise HistoryError(f"Failed to load history: {exc}") from exc


def record(base_dir: Path, action: str, encrypted_file: str,
           recipients: Optional[List[str]] = None, note: Optional[str] = None) -> HistoryEntry:
    """Append a new entry to the history log, capping at _MAX_ENTRIES."""
    entries = load_history(base_dir)
    entry = HistoryEntry(
        action=action,
        timestamp=time.time(),
        encrypted_file=encrypted_file,
        recipients=recipients or [],
        note=note,
    )
    entries.append(entry)
    if len(entries) > _MAX_ENTRIES:
        entries = entries[-_MAX_ENTRIES:]
    path = _history_path(base_dir)
    path.write_text(json.dumps([e.to_dict() for e in entries], indent=2), encoding="utf-8")
    return entry


def clear_history(base_dir: Path) -> None:
    path = _history_path(base_dir)
    if path.exists():
        path.unlink()
