"""Key rotation support for envault."""

from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

from envault.config import EnvaultConfig
from envault.crypto import encrypt_file, decrypt_file, GPGError
from envault.audit import AuditLog


class RotationError(Exception):
    """Raised when key rotation fails."""


def rotate(
    config: EnvaultConfig,
    new_recipients: list[str],
    *,
    passphrase: str | None = None,
    audit_log: AuditLog | None = None,
    dry_run: bool = False,
) -> Path:
    """Re-encrypt the vault file for a new set of recipient key IDs.

    Parameters
    ----------
    config:
        Active envault configuration.
    new_recipients:
        GPG key fingerprints / IDs to encrypt for.
    passphrase:
        Optional symmetric passphrase forwarded to GPG.
    audit_log:
        If supplied, a rotation event is appended.
    dry_run:
        When *True* the function validates inputs but does not write files.

    Returns
    -------
    Path
        Path to the newly written encrypted file.
    """
    encrypted_path = Path(config.encrypted_file)
    if not encrypted_path.exists():
        raise RotationError(f"Encrypted file not found: {encrypted_path}")

    if not new_recipients:
        raise RotationError("new_recipients must not be empty.")

    tmp_plain = encrypted_path.with_suffix(".tmp.decrypted")
    try:
        try:
            decrypt_file(encrypted_path, tmp_plain, passphrase=passphrase)
        except GPGError as exc:
            raise RotationError(f"Decryption failed during rotation: {exc}") from exc

        new_encrypted = encrypted_path.with_suffix(".rotated.gpg")
        try:
            encrypt_file(
                tmp_plain,
                new_encrypted,
                recipients=new_recipients,
                passphrase=passphrase,
            )
        except GPGError as exc:
            raise RotationError(f"Re-encryption failed during rotation: {exc}") from exc

        if not dry_run:
            backup = encrypted_path.with_suffix(".bak.gpg")
            shutil.copy2(encrypted_path, backup)
            shutil.move(str(new_encrypted), str(encrypted_path))
        else:
            new_encrypted.unlink(missing_ok=True)
    finally:
        tmp_plain.unlink(missing_ok=True)

    if audit_log and not dry_run:
        audit_log.record(
            action="rotate",
            actor="envault",
            details={
                "recipients": new_recipients,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

    return encrypted_path
