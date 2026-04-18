"""Per-environment notes attached to the encrypted vault."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional


class NoteError(Exception):
    pass


def _notes_path(config_dir: Path) -> Path:
    return config_dir / ".envault_notes.json"


def load_notes(config_dir: Path) -> List[dict]:
    path = _notes_path(config_dir)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise NoteError(f"Corrupt notes file: {exc}") from exc
    if not isinstance(data, list):
        raise NoteError("Notes file must contain a JSON array")
    return data


def save_notes(config_dir: Path, notes: List[dict]) -> None:
    _notes_path(config_dir).write_text(json.dumps(notes, indent=2))


def add_note(config_dir: Path, profile: str, text: str, author: Optional[str] = None) -> dict:
    import datetime
    notes = load_notes(config_dir)
    entry = {
        "profile": profile,
        "text": text,
        "author": author or "",
        "created_at": datetime.datetime.utcnow().isoformat(timespec="seconds"),
    }
    notes.append(entry)
    save_notes(config_dir, notes)
    return entry


def list_notes(config_dir: Path, profile: Optional[str] = None) -> List[dict]:
    notes = load_notes(config_dir)
    if profile:
        notes = [n for n in notes if n.get("profile") == profile]
    return notes


def clear_notes(config_dir: Path, profile: Optional[str] = None) -> int:
    notes = load_notes(config_dir)
    if profile:
        remaining = [n for n in notes if n.get("profile") != profile]
    else:
        remaining = []
    removed = len(notes) - len(remaining)
    save_notes(config_dir, remaining)
    return removed
