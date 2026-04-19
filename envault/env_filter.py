"""Filter .env file keys by prefix, pattern, or list."""
from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional


class FilterError(Exception):
    pass


def _parse_env(text: str) -> List[tuple]:
    """Return list of (key, raw_line) tuples; comments/blanks have key=None."""
    result = []
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            result.append((None, line))
            continue
        if "=" not in stripped:
            result.append((None, line))
            continue
        key = stripped.split("=", 1)[0].strip()
        result.append((key, line))
    return result


def filter_env(
    src: Path,
    dest: Path,
    *,
    prefix: Optional[str] = None,
    pattern: Optional[str] = None,
    keys: Optional[List[str]] = None,
    exclude: bool = False,
) -> int:
    """Write filtered keys from *src* to *dest*. Returns number of keys written."""
    if not src.exists():
        raise FilterError(f"Source file not found: {src}")
    if prefix is None and pattern is None and keys is None:
        raise FilterError("At least one of prefix, pattern, or keys must be provided.")

    compiled = re.compile(pattern) if pattern else None
    key_set = set(keys) if keys else None

    lines = _parse_env(src.read_text())
    out_lines: List[str] = []
    count = 0

    for key, raw in lines:
        if key is None:
            out_lines.append(raw)
            continue
        match = False
        if prefix and key.startswith(prefix):
            match = True
        if compiled and compiled.search(key):
            match = True
        if key_set and key in key_set:
            match = True
        if exclude:
            match = not match
        if match:
            out_lines.append(raw)
            count += 1

    dest.write_text("".join(out_lines))
    return count
