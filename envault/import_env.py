"""Import .env variables from an existing encrypted vault into the current environment."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Optional

from envault.crypto import decrypt_file, GPGError
from envault.config import EnvaultConfig


class ImportError(Exception):  # noqa: A001
    """Raised when an import operation fails."""


def _parse_env(text: str) -> Dict[str, str]:
    """Parse KEY=VALUE lines from decrypted env text."""
    result: Dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            result[key] = value
    return result


def import_env(
    config: EnvaultConfig,
    *,
    overwrite: bool = False,
    dry_run: bool = False,
    passphrase: Optional[str] = None,
    keys: Optional[list[str]] = None,
) -> Dict[str, str]:
    """Decrypt the vault and import variables into the current process environment.

    Args:
        config: Loaded EnvaultConfig.
        overwrite: If True, overwrite existing env vars. Defaults to False.
        dry_run: If True, return what would be set without modifying os.environ.
        passphrase: Optional GPG passphrase.
        keys: Optional list of specific keys to import; imports all if None.

    Returns:
        A dict of the variables that were (or would be) imported.
    """
    enc_path = Path(config.encrypted_file)
    if not enc_path.exists():
        raise ImportError(f"Encrypted file not found: {enc_path}")

    try:
        decrypted_text = decrypt_file(str(enc_path), passphrase=passphrase)
    except GPGError as exc:
        raise ImportError(f"Decryption failed: {exc}") from exc

    parsed = _parse_env(decrypted_text)

    if keys:
        missing = [k for k in keys if k not in parsed]
        if missing:
            raise ImportError(f"Requested keys not found in vault: {', '.join(missing)}")
        parsed = {k: parsed[k] for k in keys}

    imported: Dict[str, str] = {}
    for key, value in parsed.items():
        if not overwrite and key in os.environ:
            continue
        imported[key] = value
        if not dry_run:
            os.environ[key] = value

    return imported
