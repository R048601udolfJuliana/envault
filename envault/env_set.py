"""Set or update a key in a decrypted .env file."""
from __future__ import annotations

import re
from pathlib import Path


class SetError(Exception):
    pass


def _parse_env(text: str) -> list[tuple[str, str]]:
    """Return list of (line, key) tuples preserving all lines."""
    lines = []
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if stripped.startswith("#") or not stripped or "=" not in stripped:
            lines.append((line, None))
        else:
            key = stripped.split("=", 1)[0].strip()
            lines.append((line, key))
    return lines


def set_key(env_file: Path, key: str, value: str, *, create: bool = True) -> bool:
    """Set *key* to *value* in *env_file*.

    Returns True if the key was added, False if it was updated.
    Raises SetError if the file is missing and *create* is False.
    """
    if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", key):
        raise SetError(f"Invalid key name: {key!r}")

    env_file = Path(env_file)
    if not env_file.exists():
        if not create:
            raise SetError(f"File not found: {env_file}")
        env_file.write_text(f"{key}={value}\n", encoding="utf-8")
        return True

    text = env_file.read_text(encoding="utf-8")
    parsed = _parse_env(text)

    new_line = f"{key}={value}\n"
    updated = False
    result = []
    for line, lkey in parsed:
        if lkey == key:
            result.append(new_line)
            updated = True
        else:
            result.append(line)

    if not updated:
        if result and not result[-1].endswith("\n"):
            result.append("\n")
        result.append(new_line)

    env_file.write_text("".join(result), encoding="utf-8")
    return not updated


def unset_key(env_file: Path, key: str) -> bool:
    """Remove *key* from *env_file*. Returns True if removed, False if not found."""
    env_file = Path(env_file)
    if not env_file.exists():
        raise SetError(f"File not found: {env_file}")

    text = env_file.read_text(encoding="utf-8")
    parsed = _parse_env(text)
    result = [line for line, lkey in parsed if lkey != key]
    removed = len(result) < len(parsed)
    env_file.write_text("".join(result), encoding="utf-8")
    return removed
