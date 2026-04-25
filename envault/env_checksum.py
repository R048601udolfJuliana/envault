"""Checksum utilities for .env files — compute and verify SHA-256 digests."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


class ChecksumError(Exception):
    """Raised when a checksum operation fails."""


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def compute_checksum(env_file: Path) -> str:
    """Return the SHA-256 hex digest of *env_file*."""
    if not env_file.exists():
        raise ChecksumError(f"File not found: {env_file}")
    return _sha256(env_file)


def save_checksum(env_file: Path, checksum_file: Path | None = None) -> Path:
    """Compute and persist the checksum of *env_file* to a JSON sidecar.

    Returns the path to the written checksum file.
    """
    if not env_file.exists():
        raise ChecksumError(f"File not found: {env_file}")
    digest = _sha256(env_file)
    dest = checksum_file or env_file.with_suffix(".checksum.json")
    dest.write_text(json.dumps({"file": env_file.name, "sha256": digest}, indent=2))
    return dest


def verify_checksum(env_file: Path, checksum_file: Path | None = None) -> bool:
    """Return *True* if *env_file* matches its stored checksum, *False* otherwise.

    Raises :class:`ChecksumError` if either file is missing or the checksum
    file is malformed.
    """
    if not env_file.exists():
        raise ChecksumError(f"File not found: {env_file}")
    src = checksum_file or env_file.with_suffix(".checksum.json")
    if not src.exists():
        raise ChecksumError(f"Checksum file not found: {src}")
    try:
        data = json.loads(src.read_text())
        stored = data["sha256"]
    except (json.JSONDecodeError, KeyError) as exc:
        raise ChecksumError(f"Malformed checksum file: {src}") from exc
    return _sha256(env_file) == stored
