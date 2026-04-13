"""Sync encrypted .env files to/from a shared directory or remote path."""

import os
import shutil
from pathlib import Path
from typing import Optional

from envault.config import EnvaultConfig, ConfigError
from envault.crypto import encrypt_file, decrypt_file, GPGError


class SyncError(Exception):
    """Raised when a sync operation fails."""


def push(config: EnvaultConfig, env_file: str = ".env", force: bool = False) -> str:
    """
    Encrypt the local .env file and copy it to the sync destination.

    Returns the path of the encrypted file at the destination.
    """
    env_path = Path(env_file)
    if not env_path.exists():
        raise SyncError(f"Source file not found: {env_file}")

    dest_dir = Path(config.sync_path)
    dest_dir.mkdir(parents=True, exist_ok=True)

    encrypted_local = Path(config.encrypted_file)

    try:
        encrypt_file(str(env_path), str(encrypted_local), config.recipients)
    except GPGError as exc:
        raise SyncError(f"Encryption failed: {exc}") from exc

    dest_file = dest_dir / encrypted_local.name
    if dest_file.exists() and not force:
        raise SyncError(
            f"Destination file already exists: {dest_file}. Use force=True to overwrite."
        )

    shutil.copy2(str(encrypted_local), str(dest_file))
    return str(dest_file)


def pull(config: EnvaultConfig, env_file: str = ".env", force: bool = False) -> str:
    """
    Fetch the encrypted file from the sync destination and decrypt it locally.

    Returns the path of the decrypted .env file.
    """
    dest_dir = Path(config.sync_path)
    encrypted_name = Path(config.encrypted_file).name
    source_file = dest_dir / encrypted_name

    if not source_file.exists():
        raise SyncError(f"No encrypted file found at: {source_file}")

    env_path = Path(env_file)
    if env_path.exists() and not force:
        raise SyncError(
            f"Local file already exists: {env_file}. Use force=True to overwrite."
        )

    local_encrypted = Path(config.encrypted_file)
    shutil.copy2(str(source_file), str(local_encrypted))

    try:
        decrypt_file(str(local_encrypted), str(env_path))
    except GPGError as exc:
        raise SyncError(f"Decryption failed: {exc}") from exc

    return str(env_path)
