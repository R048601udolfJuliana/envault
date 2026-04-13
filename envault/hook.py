"""Git hook integration for envault."""
from __future__ import annotations

import os
import stat
from pathlib import Path

HOOK_SCRIPT = """#!/bin/sh
# envault pre-commit hook
# Prevents accidental commits of unencrypted .env files.
if git diff --cached --name-only | grep -qE '^\.env(\..*)?$'; then
    echo "[envault] ERROR: Attempting to commit a plaintext .env file."
    echo "[envault] Run 'envault push' to encrypt it first, then unstage the .env file."
    exit 1
fi
exit 0
"""

HOOK_NAME = "pre-commit"


class HookError(Exception):
    """Raised when a git hook operation fails."""


def _hooks_dir(repo_root: Path) -> Path:
    return repo_root / ".git" / "hooks"


def install_hook(repo_root: Path, force: bool = False) -> Path:
    """Install the envault pre-commit hook into *repo_root*.

    Returns the path to the installed hook file.
    Raises HookError if the hook already exists and *force* is False.
    """
    hooks_dir = _hooks_dir(repo_root)
    if not hooks_dir.is_dir():
        raise HookError(f"No .git/hooks directory found under '{repo_root}'. "
                        "Is this a git repository?")

    hook_path = hooks_dir / HOOK_NAME
    if hook_path.exists() and not force:
        raise HookError(
            f"Hook already exists at '{hook_path}'. Use force=True to overwrite."
        )

    hook_path.write_text(HOOK_SCRIPT)
    hook_path.chmod(hook_path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    return hook_path


def uninstall_hook(repo_root: Path) -> None:
    """Remove the envault pre-commit hook from *repo_root*.

    Raises HookError if the hook does not exist.
    """
    hook_path = _hooks_dir(repo_root) / HOOK_NAME
    if not hook_path.exists():
        raise HookError(f"No hook found at '{hook_path}'.")
    hook_path.unlink()


def hook_status(repo_root: Path) -> dict:
    """Return a dict describing the current hook state."""
    hook_path = _hooks_dir(repo_root) / HOOK_NAME
    installed = hook_path.exists()
    is_envault = False
    if installed:
        try:
            is_envault = "envault" in hook_path.read_text()
        except OSError:
            pass
    return {"installed": installed, "envault_managed": is_envault, "path": str(hook_path)}
