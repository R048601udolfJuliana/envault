"""Whitelist filter: keep only explicitly allowed keys in a .env file."""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional


class WhitelistError(Exception):
    """Raised when a whitelist operation fails."""


def _parse_lines(text: str) -> List[str]:
    """Return raw lines from env text, preserving comments and blanks."""
    return text.splitlines(keepends=True)


def _key_of(line: str) -> Optional[str]:
    """Return the key for a KEY=VALUE line, or None for comments/blanks."""
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None
    match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=", stripped)
    return match.group(1) if match else None


def whitelist_env(
    src: Path,
    allowed_keys: List[str],
    dest: Optional[Path] = None,
    *,
    keep_comments: bool = True,
) -> Path:
    """Keep only *allowed_keys* in *src*, writing the result to *dest*.

    Args:
        src: Source .env file.
        allowed_keys: Keys to retain.
        dest: Destination path. Defaults to *src* (in-place).
        keep_comments: When True, comment/blank lines are preserved.

    Returns:
        Resolved path to the written file.

    Raises:
        WhitelistError: If *src* does not exist or *allowed_keys* is empty.
    """
    if not src.exists():
        raise WhitelistError(f"Source file not found: {src}")
    if not allowed_keys:
        raise WhitelistError("allowed_keys must not be empty")

    allowed = set(allowed_keys)
    lines = _parse_lines(src.read_text(encoding="utf-8"))
    out: List[str] = []

    for line in lines:
        key = _key_of(line)
        if key is None:
            if keep_comments:
                out.append(line)
        elif key in allowed:
            out.append(line)

    target = dest or src
    target.write_text("".join(out), encoding="utf-8")
    return target.resolve()
