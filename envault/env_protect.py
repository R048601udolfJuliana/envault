"""env_protect.py – mark keys as protected (read-only) in a sidecar file.

Protected keys cannot be overwritten by set/patch/import unless --force is
passed.  The protection list is stored as a JSON array in
<vault_dir>/.envault_protected.json.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List


class ProtectError(Exception):
    """Raised when a protection operation fails."""


def _protect_path(vault_dir: Path) -> Path:
    return vault_dir / ".envault_protected.json"


def load_protected(vault_dir: Path) -> List[str]:
    """Return the list of currently protected keys."""
    p = _protect_path(vault_dir)
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text())
    except json.JSONDecodeError as exc:
        raise ProtectError(f"Corrupt protected-keys file: {exc}") from exc
    if not isinstance(data, list):
        raise ProtectError("Protected-keys file must contain a JSON array.")
    return [str(k) for k in data]


def save_protected(vault_dir: Path, keys: List[str]) -> None:
    """Persist *keys* as the protected list."""
    _protect_path(vault_dir).write_text(json.dumps(sorted(set(keys)), indent=2))


def protect_key(vault_dir: Path, key: str) -> None:
    """Add *key* to the protected list (idempotent)."""
    keys = load_protected(vault_dir)
    if key not in keys:
        keys.append(key)
    save_protected(vault_dir, keys)


def unprotect_key(vault_dir: Path, key: str) -> None:
    """Remove *key* from the protected list."""
    keys = load_protected(vault_dir)
    if key not in keys:
        raise ProtectError(f"Key '{key}' is not protected.")
    keys.remove(key)
    save_protected(vault_dir, keys)


def is_protected(vault_dir: Path, key: str) -> bool:
    """Return True if *key* is currently protected."""
    return key in load_protected(vault_dir)


def check_protected(vault_dir: Path, keys: List[str], force: bool = False) -> None:
    """Raise ProtectError if any of *keys* are protected and *force* is False."""
    if force:
        return
    protected = load_protected(vault_dir)
    blocked = [k for k in keys if k in protected]
    if blocked:
        raise ProtectError(
            "The following keys are protected and cannot be modified "
            f"without --force: {', '.join(blocked)}"
        )
