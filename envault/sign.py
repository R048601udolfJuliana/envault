"""GPG signing and verification for encrypted vault files."""
from __future__ import annotations

import subprocess
from pathlib import Path


class SignError(Exception):
    pass


def sign_file(file_path: Path, key_id: str, sig_path: Path | None = None) -> Path:
    """Create a detached GPG signature for *file_path*.

    Returns the path to the .sig file.
    """
    if not file_path.exists():
        raise SignError(f"File not found: {file_path}")

    sig_path = sig_path or file_path.with_suffix(file_path.suffix + ".sig")

    cmd = [
        "gpg",
        "--batch",
        "--yes",
        "--local-user", key_id,
        "--detach-sign",
        "--output", str(sig_path),
        str(file_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise SignError(f"GPG signing failed: {result.stderr.strip()}")

    return sig_path


def verify_signature(file_path: Path, sig_path: Path | None = None) -> str:
    """Verify a detached GPG signature.

    Returns the signer key-id string on success.
    Raises SignError on failure.
    """
    if not file_path.exists():
        raise SignError(f"File not found: {file_path}")

    sig_path = sig_path or file_path.with_suffix(file_path.suffix + ".sig")
    if not sig_path.exists():
        raise SignError(f"Signature file not found: {sig_path}")

    cmd = ["gpg", "--batch", "--verify", str(sig_path), str(file_path)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise SignError(f"Signature verification failed: {result.stderr.strip()}")

    # Extract key id from stderr output
    for line in result.stderr.splitlines():
        if "key" in line.lower():
            parts = line.split()
            for i, part in enumerate(parts):
                if part.lower() == "key" and i + 1 < len(parts):
                    return parts[i + 1].lstrip("ID").strip()
    return "unknown"
