"""Pin management: lock a project to a specific snapshot or encrypted file hash."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Optional

PIN_FILE = ".envault-pin"


class PinError(Exception):
    pass


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def pin_file(encrypted_path: Path, pin_path: Path | None = None) -> str:
    """Record the SHA-256 of *encrypted_path* into the pin file."""
    if not encrypted_path.exists():
        raise PinError(f"Encrypted file not found: {encrypted_path}")
    digest = _sha256(encrypted_path)
    target = Path(pin_path or PIN_FILE)
    target.write_text(json.dumps({"file": str(encrypted_path), "sha256": digest}, indent=2))
    return digest


def check_pin(encrypted_path: Path, pin_path: Path | None = None) -> bool:
    """Return True if *encrypted_path* matches the recorded pin."""
    target = Path(pin_path or PIN_FILE)
    if not target.exists():
        raise PinError(f"Pin file not found: {target}")
    try:
        data = json.loads(target.read_text())
    except json.JSONDecodeError as exc:
        raise PinError(f"Corrupt pin file: {exc}") from exc
    if "sha256" not in data:
        raise PinError("Pin file missing 'sha256' field")
    if not encrypted_path.exists():
        raise PinError(f"Encrypted file not found: {encrypted_path}")
    return _sha256(encrypted_path) == data["sha256"]


def load_pin(pin_path: Path | None = None) -> Optional[dict]:
    """Return the pin data dict or None if no pin file exists."""
    target = Path(pin_path or PIN_FILE)
    if not target.exists():
        return None
    try:
        return json.loads(target.read_text())
    except json.JSONDecodeError as exc:
        raise PinError(f"Corrupt pin file: {exc}") from exc


def remove_pin(pin_path: Path | None = None) -> bool:
    """Delete the pin file. Returns True if it existed."""
    target = Path(pin_path or PIN_FILE)
    if target.exists():
        target.unlink()
        return True
    return False
