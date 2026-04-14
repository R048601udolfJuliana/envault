"""Backup and restore encrypted .env vault files."""
from __future__ import annotations

import shutil
import time
from pathlib import Path
from typing import List


class BackupError(Exception):
    """Raised when a backup or restore operation fails."""


_BACKUP_SUFFIX = ".bak"
_TS_FORMAT = "%Y%m%d_%H%M%S"


def _backup_dir(base: Path) -> Path:
    return base / ".envault_backups"


def create_backup(encrypted_file: Path, backup_root: Path | None = None) -> Path:
    """Copy *encrypted_file* into the backup directory with a timestamp suffix.

    Returns the path of the newly created backup file.
    """
    src = Path(encrypted_file)
    if not src.exists():
        raise BackupError(f"Encrypted file not found: {src}")

    root = Path(backup_root) if backup_root else src.parent
    bdir = _backup_dir(root)
    bdir.mkdir(parents=True, exist_ok=True)

    ts = time.strftime(_TS_FORMAT)
    dest = bdir / f"{src.name}_{ts}{_BACKUP_SUFFIX}"
    shutil.copy2(src, dest)
    return dest


def list_backups(encrypted_file: Path, backup_root: Path | None = None) -> List[Path]:
    """Return all backup files for *encrypted_file*, sorted oldest-first."""
    src = Path(encrypted_file)
    root = Path(backup_root) if backup_root else src.parent
    bdir = _backup_dir(root)

    if not bdir.exists():
        return []

    prefix = src.name + "_"
    matches = sorted(
        p for p in bdir.iterdir()
        if p.name.startswith(prefix) and p.suffix == _BACKUP_SUFFIX
    )
    return matches


def restore_backup(backup_file: Path, encrypted_file: Path) -> None:
    """Overwrite *encrypted_file* with the contents of *backup_file*."""
    bak = Path(backup_file)
    if not bak.exists():
        raise BackupError(f"Backup file not found: {bak}")

    dest = Path(encrypted_file)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(bak, dest)


def delete_backup(backup_file: Path) -> None:
    """Delete a specific backup file."""
    bak = Path(backup_file)
    if not bak.exists():
        raise BackupError(f"Backup file not found: {bak}")
    bak.unlink()
