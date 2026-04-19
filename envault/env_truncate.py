"""Truncate .env file to a maximum number of keys."""
from __future__ import annotations

from pathlib import Path
from typing import List, Tuple


class TruncateError(Exception):
    pass


def _parse_blocks(text: str) -> List[str]:
    """Return non-comment, non-blank lines that are key=value pairs."""
    blocks = []
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            blocks.append(line)
    return blocks


def truncate_env(
    src: Path,
    dest: Path | None = None,
    max_keys: int = 10,
    from_end: bool = False,
) -> Tuple[int, int]:
    """Truncate *src* to at most *max_keys* key=value entries.

    Args:
        src: Source .env file.
        dest: Destination file; defaults to *src* (in-place).
        max_keys: Maximum number of keys to keep.
        from_end: If True keep the *last* max_keys entries instead of first.

    Returns:
        Tuple of (original_count, kept_count).
    """
    if max_keys < 1:
        raise TruncateError("max_keys must be >= 1")

    if not src.exists():
        raise TruncateError(f"File not found: {src}")

    text = src.read_text(encoding="utf-8")
    all_lines = text.splitlines(keepends=True)

    kv_lines = _parse_blocks(text)
    original_count = len(kv_lines)

    kept = kv_lines[-max_keys:] if from_end else kv_lines[:max_keys]
    kept_set = set(id(l) for l in kept)

    # Rebuild: keep comment/blank lines plus kept kv lines (preserve order)
    kept_kv_remaining = list(kept)
    output_lines: List[str] = []
    for line in all_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            output_lines.append(line)
        elif "=" in stripped:
            if kept_kv_remaining and line == kept_kv_remaining[0]:
                output_lines.append(line)
                kept_kv_remaining.pop(0)
            # else skip

    target = dest if dest is not None else src
    target.write_text("".join(output_lines), encoding="utf-8")
    return original_count, len(kept)
