"""Apply a patch (set of key-value overrides) to a .env file in-place or to a destination."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional


class PatchError(Exception):
    """Raised when patching fails."""


def _parse_env(text: str) -> list[tuple[str, str]]:
    """Return list of (raw_line, key) tuples preserving order."""
    lines = []
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if stripped.startswith("#") or not stripped:
            lines.append((line, ""))
            continue
        if "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            lines.append((line, key))
        else:
            lines.append((line, ""))
    return lines


def patch_env(
    src: Path,
    overrides: Dict[str, str],
    dest: Optional[Path] = None,
    *,
    add_missing: bool = True,
) -> Path:
    """Apply *overrides* to *src* and write the result.

    Parameters
    ----------
    src:          Source .env file.
    overrides:    Mapping of key -> new value to apply.
    dest:         Destination path.  Defaults to *src* (in-place).
    add_missing:  When True, keys not already present are appended.

    Returns the path that was written.
    """
    if not src.exists():
        raise PatchError(f"Source file not found: {src}")
    if not overrides:
        raise PatchError("No overrides provided.")

    dest = dest or src
    text = src.read_text(encoding="utf-8")
    parsed = _parse_env(text)

    applied: set[str] = set()
    new_lines: list[str] = []

    for raw_line, key in parsed:
        if key and key in overrides:
            value = overrides[key]
            new_lines.append(f"{key}={value}\n")
            applied.add(key)
        else:
            new_lines.append(raw_line if raw_line.endswith("\n") else raw_line)

    if add_missing:
        for key, value in overrides.items():
            if key not in applied:
                new_lines.append(f"{key}={value}\n")

    dest.write_text("".join(new_lines), encoding="utf-8")
    return dest
