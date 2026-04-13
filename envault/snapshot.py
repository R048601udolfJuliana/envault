"""Snapshot management: save and restore named snapshots of encrypted .env files."""

from __future__ import annotations

import shutil
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict

SNAPSHOT_DIR_NAME = ".envault_snapshots"
META_FILE = "snapshots.json"


class SnapshotError(Exception):
    """Raised when a snapshot operation fails."""


def _snapshot_dir(base: Path) -> Path:
    return base / SNAPSHOT_DIR_NAME


def _meta_path(base: Path) -> Path:
    return _snapshot_dir(base) / META_FILE


def _load_meta(base: Path) -> List[Dict]:
    meta = _meta_path(base)
    if not meta.exists():
        return []
    try:
        return json.loads(meta.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        raise SnapshotError(f"Failed to read snapshot metadata: {exc}") from exc


def _save_meta(base: Path, entries: List[Dict]) -> None:
    meta = _meta_path(base)
    meta.write_text(json.dumps(entries, indent=2))


def save_snapshot(encrypted_file: Path, name: str, base: Path | None = None) -> Dict:
    """Save a named snapshot of *encrypted_file*. Returns the metadata entry."""
    if not encrypted_file.exists():
        raise SnapshotError(f"Encrypted file not found: {encrypted_file}")

    base = base or encrypted_file.parent
    snap_dir = _snapshot_dir(base)
    snap_dir.mkdir(parents=True, exist_ok=True)

    entries = _load_meta(base)
    if any(e["name"] == name for e in entries):
        raise SnapshotError(f"Snapshot '{name}' already exists. Delete it first.")

    timestamp = datetime.now(timezone.utc).isoformat()
    filename = f"{name}_{timestamp.replace(':', '-')}{encrypted_file.suffix}.gpg"
    dest = snap_dir / filename
    shutil.copy2(encrypted_file, dest)

    entry = {"name": name, "timestamp": timestamp, "file": filename}
    entries.append(entry)
    _save_meta(base, entries)
    return entry


def restore_snapshot(name: str, target: Path, base: Path) -> None:
    """Restore a named snapshot to *target*."""
    entries = _load_meta(base)
    entry = next((e for e in entries if e["name"] == name), None)
    if entry is None:
        raise SnapshotError(f"Snapshot '{name}' not found.")

    src = _snapshot_dir(base) / entry["file"]
    if not src.exists():
        raise SnapshotError(f"Snapshot file missing on disk: {src}")

    shutil.copy2(src, target)


def list_snapshots(base: Path) -> List[Dict]:
    """Return all snapshot metadata entries."""
    return _load_meta(base)


def delete_snapshot(name: str, base: Path) -> None:
    """Delete a named snapshot and its file."""
    entries = _load_meta(base)
    entry = next((e for e in entries if e["name"] == name), None)
    if entry is None:
        raise SnapshotError(f"Snapshot '{name}' not found.")

    snap_file = _snapshot_dir(base) / entry["file"]
    if snap_file.exists():
        snap_file.unlink()

    entries = [e for e in entries if e["name"] != name]
    _save_meta(base, entries)
