"""Rename a key inside a decrypted .env file."""
from __future__ import annotations

import re
from pathlib import Path


class RenameError(Exception):
    """Raised when a rename operation fails."""


def _parse_env(text: str) -> list[tuple[str, str]]:
    """Return list of (key, raw_line) pairs, preserving comments/blanks as (None, line)."""
    lines = []
    for line in text.splitlines(keepends=True):
        m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)\s*=', line)
        if m:
            lines.append((m.group(1), line))
        else:
            lines.append((None, line))
    return lines


def rename_key(env_file: Path, old_key: str, new_key: str) -> int:
    """Rename *old_key* to *new_key* in *env_file*.

    Returns the number of lines changed (0 or 1).
    Raises RenameError if the file is missing or old_key not found.
    """
    if not env_file.exists():
        raise RenameError(f"File not found: {env_file}")
    if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', new_key):
        raise RenameError(f"Invalid key name: {new_key!r}")

    text = env_file.read_text()
    parsed = _parse_env(text)

    keys = [k for k, _ in parsed if k is not None]
    if old_key not in keys:
        raise RenameError(f"Key {old_key!r} not found in {env_file}")
    if new_key in keys and new_key != old_key:
        raise RenameError(f"Key {new_key!r} already exists in {env_file}")

    changed = 0
    new_lines = []
    for key, line in parsed:
        if key == old_key:
            new_line = re.sub(r'^' + re.escape(old_key), new_key, line, count=1)
            new_lines.append(new_line)
            changed += 1
        else:
            new_lines.append(line)

    env_file.write_text(''.join(new_lines))
    return changed
