"""Trim leading/trailing whitespace from .env values."""
from __future__ import annotations

from pathlib import Path
from typing import List, Tuple


class TrimError(Exception):
    """Raised when trimming fails."""


def _parse_lines(text: str) -> List[Tuple[str, str, bool]]:
    """Return list of (raw_line, trimmed_line, was_changed)."""
    result = []
    for line in text.splitlines(keepends=True):
        stripped = line.rstrip("\n")
        if not stripped or stripped.lstrip().startswith("#") or "=" not in stripped:
            result.append((line, line, False))
            continue
        key, _, value = stripped.partition("=")
        trimmed_value = value.strip()
        trimmed_line = f"{key}={trimmed_value}\n"
        changed = trimmed_line != line
        result.append((line, trimmed_line, changed))
    return result


def trim_env(
    src: Path,
    dest: Path | None = None,
    *,
    dry_run: bool = False,
) -> int:
    """Trim whitespace from values in *src*.

    Returns the number of lines changed.
    Writes in-place when *dest* is ``None`` unless *dry_run* is ``True``.
    """
    if not src.exists():
        raise TrimError(f"File not found: {src}")

    text = src.read_text(encoding="utf-8")
    parsed = _parse_lines(text)
    changed_count = sum(1 for _, _, changed in parsed if changed)

    if not dry_run:
        out_path = dest if dest is not None else src
        out_path.write_text("".join(line for _, line, _ in parsed), encoding="utf-8")

    return changed_count
