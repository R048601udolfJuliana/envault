"""Passphrase management utilities for envault.

Provides helpers for prompting, validating, and caching passphrases
used during GPG symmetric encryption/decryption operations.
"""

from __future__ import annotations

import getpass
import os
from typing import Optional


class PassphraseError(Exception):
    """Raised when passphrase validation or retrieval fails."""


_ENV_VAR = "ENVAULT_PASSPHRASE"
_MIN_LENGTH = 8


def get_passphrase(prompt: str = "Passphrase: ", confirm: bool = False) -> str:
    """Retrieve a passphrase from the environment or by prompting the user.

    If the ``ENVAULT_PASSPHRASE`` environment variable is set its value is
    returned directly without prompting.  When *confirm* is ``True`` the user
    is asked to enter the passphrase twice and the two values must match.

    Raises:
        PassphraseError: If the passphrase is too short or confirmation fails.
    """
    env_value = os.environ.get(_ENV_VAR)
    if env_value is not None:
        _validate(env_value)
        return env_value

    passphrase = getpass.getpass(prompt)
    _validate(passphrase)

    if confirm:
        confirmation = getpass.getpass("Confirm passphrase: ")
        if passphrase != confirmation:
            raise PassphraseError("Passphrases do not match.")

    return passphrase


def _validate(passphrase: str) -> None:
    """Raise *PassphraseError* if *passphrase* does not meet requirements."""
    if not passphrase:
        raise PassphraseError("Passphrase must not be empty.")
    if len(passphrase) < _MIN_LENGTH:
        raise PassphraseError(
            f"Passphrase must be at least {_MIN_LENGTH} characters long."
        )


def passphrase_from_env() -> Optional[str]:
    """Return the passphrase stored in the environment variable, or ``None``."""
    return os.environ.get(_ENV_VAR)
