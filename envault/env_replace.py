"""envault.env_replace – find-and-replace values inside a .env file."""
from __future__ import annotations

import re
from pathlib import Path
from typing import List, Tuple


class ReplaceError(Exception):
    """Raised when a replace operation fails."""


def _parse_lines(text: str) -> List[str]:
    return text.splitlines(keepends=True)


def _strip_quotes(value: str) -> str:
    for q in ('"', "'"):
        if value.startswith(q) and value.endswith(q) and len(value) >= 2:
            return value[1:-1]
    return value


def replace_value(
    src: Path,
    pattern: str,
    replacement: str,
    *,
    dest: Path | None = None,
    keys: List[str] | None = None,
    literal: bool = False,
    count: int = 0,
) -> Tuple[Path, int]:
    """Replace occurrences of *pattern* in env values.

    Args:
        src: Source .env file.
        pattern: Regex (or literal string when *literal* is True) to match.
        replacement: Replacement string.
        dest: Output file; defaults to *src* (in-place).
        keys: If provided, only replace in these keys.
        literal: Treat *pattern* as a plain string, not a regex.
        count: Maximum replacements per line (0 = unlimited).

    Returns:
        Tuple of (resolved destination path, number of lines changed).
    """
    if not src.exists():
        raise ReplaceError(f"Source file not found: {src}")

    flags = re.IGNORECASE if not literal else 0
    rx = re.compile(re.escape(pattern) if literal else pattern, flags)

    lines = _parse_lines(src.read_text(encoding="utf-8"))
    out: List[str] = []
    changed = 0

    for line in lines:
        stripped = line.rstrip("\n")
        if "=" not in stripped or stripped.lstrip().startswith("#"):
            out.append(line)
            continue

        key, _, raw_val = stripped.partition("=")
        key = key.strip()

        if keys is not None and key not in keys:
            out.append(line)
            continue

        bare = _strip_quotes(raw_val)
        new_bare, n = rx.subn(replacement, bare, count=count)
        if n:
            changed += 1
            eol = "\n" if line.endswith("\n") else ""
            out.append(f"{key}={new_bare}{eol}")
        else:
            out.append(line)

    resolved = dest or src
    resolved.write_text("".join(out), encoding="utf-8")
    return resolved, changed
