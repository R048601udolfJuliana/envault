"""Normalize .env key casing — convert all keys to UPPER_CASE."""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple


class UpperError(Exception):
    """Raised when key normalization fails."""


def _parse_lines(text: str) -> List[Tuple[str, str]]:
    """Return list of (original_line, normalized_line) pairs."""
    result: List[Tuple[str, str]] = []
    for line in text.splitlines(keepends=True):
        stripped = line.rstrip("\n")
        # Preserve blank lines and comments unchanged
        if not stripped or stripped.lstrip().startswith("#"):
            result.append((line, line))
            continue
        if "=" not in stripped:
            result.append((line, line))
            continue
        key, _, value = stripped.partition("=")
        upper_key = key.upper()
        newline_char = "\n" if line.endswith("\n") else ""
        normalized = f"{upper_key}={value}{newline_char}"
        result.append((line, normalized))
    return result


def upper_env(
    src: Path,
    dest: Path | None = None,
    *,
    dry_run: bool = False,
) -> List[str]:
    """Convert all keys in *src* to UPPER_CASE.

    Parameters
    ----------
    src:
        Path to the source .env file.
    dest:
        Destination path.  Defaults to *src* (in-place).
    dry_run:
        If ``True``, return the list of changed lines without writing.

    Returns
    -------
    List of lines that were changed (empty means nothing to do).
    """
    if not src.exists():
        raise UpperError(f"Source file not found: {src}")

    text = src.read_text(encoding="utf-8")
    pairs = _parse_lines(text)

    changed = [orig for orig, norm in pairs if orig != norm]
    if dry_run or not changed:
        return changed

    out_path = dest if dest is not None else src
    out_path.write_text("".join(norm for _, norm in pairs), encoding="utf-8")
    return changed
