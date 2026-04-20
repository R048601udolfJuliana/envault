"""Lowercase key normalisation for .env files.

Converts all environment variable keys to lowercase, optionally
writing the result to a destination file.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Tuple


class LowercaseError(Exception):
    """Raised when key lowercasing fails."""


# (prefix, key, separator, value)  — prefix holds comments / blank lines
_LINE_RE = re.compile(r'^([A-Za-z_][A-Za-z0-9_]*)(\s*=\s*)(.*)$')


def _parse_lines(text: str) -> List[Tuple[str, bool]]:
    """Return list of (transformed_line, was_changed) tuples."""
    results: List[Tuple[str, bool]] = []
    for raw in text.splitlines(keepends=True):
        stripped = raw.rstrip('\n')
        m = _LINE_RE.match(stripped)
        if m:
            key, sep, val = m.group(1), m.group(2), m.group(3)
            lower_key = key.lower()
            changed = lower_key != key
            suffix = '\n' if raw.endswith('\n') else ''
            results.append((f"{lower_key}{sep}{val}{suffix}", changed))
        else:
            results.append((raw, False))
    return results


def lowercase_env(
    src: Path,
    dest: Path | None = None,
    *,
    dry_run: bool = False,
) -> List[str]:
    """Lowercase all keys in *src* and write to *dest* (default: in-place).

    Returns a list of keys that were changed.

    Raises:
        LowercaseError: if *src* does not exist.
    """
    if not src.exists():
        raise LowercaseError(f"File not found: {src}")

    text = src.read_text(encoding="utf-8")
    parsed = _parse_lines(text)

    changed_keys: List[str] = []
    output_lines: List[str] = []
    for line, was_changed in parsed:
        output_lines.append(line)
        if was_changed:
            # Extract the key from the transformed line
            m = _LINE_RE.match(line.rstrip('\n'))
            if m:
                changed_keys.append(m.group(1))

    if not dry_run:
        target = dest if dest is not None else src
        target.write_text("".join(output_lines), encoding="utf-8")

    return changed_keys
