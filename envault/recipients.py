"""Manage GPG recipient keys for envault encryption."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from envault.keys import GPGKey, list_public_keys


class RecipientsError(Exception):
    """Raised when recipient management fails."""


RECIPIENTS_FILE = ".envault-recipients"


def load_recipients(base_dir: Path | None = None) -> List[str]:
    """Load recipient key fingerprints from the recipients file.

    Args:
        base_dir: Directory containing the recipients file. Defaults to cwd.

    Returns:
        List of GPG fingerprints.
    """
    path = (base_dir or Path.cwd()) / RECIPIENTS_FILE
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
        return data.get("recipients", [])
    except (json.JSONDecodeError, OSError) as exc:
        raise RecipientsError(f"Failed to read recipients file: {exc}") from exc


def save_recipients(fingerprints: List[str], base_dir: Path | None = None) -> None:
    """Persist recipient fingerprints to the recipients file.

    Args:
        fingerprints: List of GPG fingerprints to save.
        base_dir: Directory for the recipients file. Defaults to cwd.
    """
    path = (base_dir or Path.cwd()) / RECIPIENTS_FILE
    try:
        path.write_text(json.dumps({"recipients": fingerprints}, indent=2))
    except OSError as exc:
        raise RecipientsError(f"Failed to write recipients file: {exc}") from exc


def add_recipient(fingerprint: str, base_dir: Path | None = None) -> List[str]:
    """Add a recipient fingerprint if not already present.

    Args:
        fingerprint: GPG fingerprint to add.
        base_dir: Directory for the recipients file.

    Returns:
        Updated list of fingerprints.
    """
    current = load_recipients(base_dir)
    if fingerprint in current:
        return current
    current.append(fingerprint)
    save_recipients(current, base_dir)
    return current


def remove_recipient(fingerprint: str, base_dir: Path | None = None) -> List[str]:
    """Remove a recipient fingerprint.

    Args:
        fingerprint: GPG fingerprint to remove.
        base_dir: Directory for the recipients file.

    Returns:
        Updated list of fingerprints.

    Raises:
        RecipientsError: If the fingerprint is not in the list.
    """
    current = load_recipients(base_dir)
    if fingerprint not in current:
        raise RecipientsError(f"Recipient {fingerprint!r} not found.")
    current.remove(fingerprint)
    save_recipients(current, base_dir)
    return current


def resolve_recipients(base_dir: Path | None = None) -> List[GPGKey]:
    """Return GPGKey objects for all stored recipient fingerprints.

    Only fingerprints that match a key available in the local keyring are returned.
    """
    fingerprints = load_recipients(base_dir)
    available = {key.fingerprint: key for key in list_public_keys()}
    return [available[fp] for fp in fingerprints if fp in available]
