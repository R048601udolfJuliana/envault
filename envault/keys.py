"""Key management utilities for envault."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from typing import List, Optional

from envault.crypto import GPGError, _gpg_available


class KeyError(Exception):  # noqa: A001
    """Raised when a key operation fails."""


@dataclass
class GPGKey:
    """Represents a GPG key entry."""

    fingerprint: str
    uids: List[str] = field(default_factory=list)
    key_type: str = "pub"  # 'pub' or 'sec'

    @property
    def short_id(self) -> str:
        """Return the last 16 characters of the fingerprint."""
        return self.fingerprint[-16:]

    def __str__(self) -> str:
        uid_str = ", ".join(self.uids) if self.uids else "<no UID>"
        return f"{self.short_id}  {uid_str}"


def list_public_keys(pattern: Optional[str] = None) -> List[GPGKey]:
    """Return public keys from the local GPG keyring.

    Args:
        pattern: Optional search string (email, name, fingerprint fragment).

    Returns:
        List of :class:`GPGKey` objects.

    Raises:
        KeyError: If GPG is unavailable or the command fails.
    """
    if not _gpg_available():
        raise KeyError("GPG executable not found. Please install GPG.")

    cmd = ["gpg", "--batch", "--with-colons", "--fingerprint", "--list-keys"]
    if pattern:
        cmd.append(pattern)

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise KeyError(f"GPG list-keys failed: {result.stderr.strip()}")

    return _parse_colon_output(result.stdout, key_type="pub")


def import_key(key_data: str) -> str:
    """Import an ASCII-armored GPG public key.

    Args:
        key_data: ASCII-armored key block as a string.

    Returns:
        Fingerprint of the imported key.

    Raises:
        KeyError: If the import fails.
    """
    if not _gpg_available():
        raise KeyError("GPG executable not found. Please install GPG.")

    result = subprocess.run(
        ["gpg", "--batch", "--import"],
        input=key_data,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise KeyError(f"GPG import failed: {result.stderr.strip()}")

    # gpg writes import info to stderr
    for line in result.stderr.splitlines():
        if "key" in line.lower() and ":" in line:
            parts = line.split()
            for part in parts:
                if len(part) >= 16 and all(c in "0123456789ABCDEFabcdef" for c in part.rstrip(":")):
                    return part.rstrip(":")
    return ""


def _parse_colon_output(output: str, key_type: str = "pub") -> List[GPGKey]:
    """Parse GPG --with-colons output into GPGKey objects."""
    keys: List[GPGKey] = []
    current: Optional[GPGKey] = None

    for line in output.splitlines():
        fields = line.split(":")
        record = fields[0] if fields else ""

        if record == key_type:
            current = GPGKey(fingerprint="", key_type=key_type)
            keys.append(current)
        elif record == "fpr" and current is not None:
            current.fingerprint = fields[9] if len(fields) > 9 else ""
        elif record == "uid" and current is not None:
            uid = fields[9] if len(fields) > 9 else ""
            if uid:
                current.uids.append(uid)

    return [k for k in keys if k.fingerprint]
