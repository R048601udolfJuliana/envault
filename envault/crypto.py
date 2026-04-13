"""GPG encryption and decryption utilities for envault."""

import subprocess
import shutil
from pathlib import Path
from typing import Optional


class GPGError(Exception):
    """Raised when a GPG operation fails."""
    pass


def _gpg_available() -> bool:
    """Check if gpg binary is available on the system."""
    return shutil.which("gpg") is not None


def encrypt_file(input_path: Path, output_path: Path, recipient: str) -> None:
    """
    Encrypt a file using GPG for a given recipient key.

    Args:
        input_path: Path to the plaintext file.
        output_path: Path where the encrypted file will be written.
        recipient: GPG key ID or email of the recipient.

    Raises:
        GPGError: If encryption fails or gpg is not available.
    """
    if not _gpg_available():
        raise GPGError("gpg binary not found. Please install GnuPG.")

    cmd = [
        "gpg",
        "--batch",
        "--yes",
        "--trust-model", "always",
        "--output", str(output_path),
        "--encrypt",
        "--recipient", recipient,
        str(input_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise GPGError(f"Encryption failed: {result.stderr.strip()}")


def decrypt_file(input_path: Path, output_path: Path, passphrase: Optional[str] = None) -> None:
    """
    Decrypt a GPG-encrypted file.

    Args:
        input_path: Path to the encrypted file.
        output_path: Path where the decrypted file will be written.
        passphrase: Optional passphrase for the private key.

    Raises:
        GPGError: If decryption fails or gpg is not available.
    """
    if not _gpg_available():
        raise GPGError("gpg binary not found. Please install GnuPG.")

    cmd = [
        "gpg",
        "--batch",
        "--yes",
        "--output", str(output_path),
        "--decrypt",
        str(input_path),
    ]

    if passphrase:
        cmd = ["gpg", "--batch", "--yes", "--passphrase", passphrase,
               "--pinentry-mode", "loopback",
               "--output", str(output_path), "--decrypt", str(input_path)]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise GPGError(f"Decryption failed: {result.stderr.strip()}")


def list_keys() -> list[dict]:
    """
    List available GPG public keys.

    Returns:
        A list of dicts with 'key_id' and 'uid' fields.
    """
    if not _gpg_available():
        raise GPGError("gpg binary not found. Please install GnuPG.")

    result = subprocess.run(
        ["gpg", "--list-keys", "--with-colons"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise GPGError(f"Failed to list keys: {result.stderr.strip()}")

    keys = []
    current_key_id = None
    for line in result.stdout.splitlines():
        parts = line.split(":")
        if parts[0] == "pub":
            current_key_id = parts[4][-8:] if len(parts) > 4 else None
        elif parts[0] == "uid" and current_key_id:
            keys.append({"key_id": current_key_id, "uid": parts[9]})
    return keys
