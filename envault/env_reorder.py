"""Reorder keys in a .env file according to a given key order list."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional


class ReorderError(Exception):
    """Raised when reordering fails."""


def _parse_blocks(text: str) -> List[str]:
    """Split env text into logical blocks (comment+key or standalone comment/blank)."""
    blocks: List[str] = []
    pending: List[str] = []
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if stripped.startswith("#") or stripped == "":
            pending.append(line)
        else:
            pending.append(line)
            blocks.append("".join(pending))
            pending = []
    if pending:
        blocks.append("".join(pending))
    return blocks


def _key_of_block(block: str) -> Optional[str]:
    """Return the key name of a block, or None if it has no assignment."""
    for line in block.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            return stripped.split("=", 1)[0].strip()
    return None


def reorder_env(
    src: Path,
    order: List[str],
    dest: Optional[Path] = None,
    *,
    append_unmatched: bool = True,
) -> Path:
    """Reorder keys in *src* according to *order*.

    Keys not listed in *order* are appended at the end when
    *append_unmatched* is True (default), otherwise they are dropped.

    Args:
        src: Source .env file.
        order: Desired key order.
        dest: Destination path. Defaults to *src* (in-place).
        append_unmatched: Whether to keep keys absent from *order*.

    Returns:
        Resolved destination path.

    Raises:
        ReorderError: If *src* does not exist.
    """
    src = Path(src).resolve()
    if not src.exists():
        raise ReorderError(f"Source file not found: {src}")

    dest = Path(dest).resolve() if dest else src
    text = src.read_text(encoding="utf-8")
    blocks = _parse_blocks(text)

    keyed: dict[str, str] = {}
    unkeyed: List[str] = []
    for block in blocks:
        key = _key_of_block(block)
        if key is not None:
            keyed[key] = block
        else:
            unkeyed.append(block)

    result: List[str] = []
    # Leading unkeyed blocks (blanks/comments at top of file)
    result.extend(unkeyed)

    seen: set[str] = set()
    for k in order:
        if k in keyed:
            result.append(keyed[k])
            seen.add(k)

    if append_unmatched:
        for k, block in keyed.items():
            if k not in seen:
                result.append(block)

    dest.write_text("".join(result), encoding="utf-8")
    return dest
