"""Audit log for envault operations (push/pull/key events)."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

DEFAULT_AUDIT_FILE = ".envault_audit.log"


@dataclass
class AuditEntry:
    action: str  # e.g. "push", "pull", "key_add", "key_remove"
    actor: str   # GPG key fingerprint or username
    target: str  # file path or key id
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    details: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "action": self.action,
            "actor": self.actor,
            "target": self.target,
            "timestamp": self.timestamp,
            "details": self.details,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AuditEntry":
        return cls(
            action=data["action"],
            actor=data["actor"],
            target=data["target"],
            timestamp=data.get("timestamp", ""),
            details=data.get("details"),
        )


class AuditLog:
    def __init__(self, log_path: Optional[str] = None) -> None:
        self.log_path = Path(log_path or DEFAULT_AUDIT_FILE)

    def record(self, entry: AuditEntry) -> None:
        """Append an audit entry to the log file."""
        with self.log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry.to_dict()) + "\n")

    def read_all(self) -> List[AuditEntry]:
        """Read and return all audit entries from the log file."""
        if not self.log_path.exists():
            return []
        entries: List[AuditEntry] = []
        with self.log_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        entries.append(AuditEntry.from_dict(json.loads(line)))
                    except (json.JSONDecodeError, KeyError):
                        continue
        return entries

    def clear(self) -> None:
        """Remove the audit log file if it exists."""
        if self.log_path.exists():
            self.log_path.unlink()
