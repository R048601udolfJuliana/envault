"""Verify the integrity of an encrypted .env vault file."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Optional

from envault.config import EnvaultConfig


class VerifyError(Exception):
    """Raised when vault verification fails."""


_MANIFEST_SUFFIX = ".manifest.json"


def _sha256(path: Path) -> str:
    """Return the hex SHA-256 digest of *path*."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_manifest(config: EnvaultConfig, encrypted_path: Optional[Path] = None) -> Path:
    """Write a manifest file alongside the encrypted vault.

    Returns the path to the written manifest.
    """
    enc_path = Path(encrypted_path) if encrypted_path else Path(config.encrypted_file)
    if not enc_path.exists():
        raise VerifyError(f"Encrypted file not found: {enc_path}")

    digest = _sha256(enc_path)
    manifest = {
        "file": enc_path.name,
        "sha256": digest,
    }
    manifest_path = enc_path.with_suffix("").with_suffix("") if enc_path.suffix == ".gpg" else enc_path
    manifest_path = Path(str(enc_path) + ".manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2))
    return manifest_path


def verify_manifest(config: EnvaultConfig, encrypted_path: Optional[Path] = None) -> bool:
    """Verify the encrypted vault against its manifest.

    Returns True if the digest matches.
    Raises VerifyError if the manifest is missing or digest mismatches.
    """
    enc_path = Path(encrypted_path) if encrypted_path else Path(config.encrypted_file)
    manifest_path = Path(str(enc_path) + ".manifest.json")

    if not manifest_path.exists():
        raise VerifyError(f"Manifest not found: {manifest_path}")
    if not enc_path.exists():
        raise VerifyError(f"Encrypted file not found: {enc_path}")

    manifest = json.loads(manifest_path.read_text())
    expected = manifest.get("sha256")
    if not expected:
        raise VerifyError("Manifest is missing 'sha256' field.")

    actual = _sha256(enc_path)
    if actual != expected:
        raise VerifyError(
            f"Digest mismatch for {enc_path.name}:\n"
            f"  expected: {expected}\n"
            f"  actual:   {actual}"
        )
    return True
