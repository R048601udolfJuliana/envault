"""Sort keys in a .env file alphabetically or by group."""
from __future__ import annotations

import re
from pathlib import Path


class SortError(Exception):
    pass


def _parse_blocks(text: str) -> list[tuple[str, str]]:
    """Return list of (comment_header, key=value) pairs."""
    blocks: list[tuple[str, str]] = []
    pending_comment = ""
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            pending_comment = ""
            continue
        if stripped.startswith("#"):
            pending_comment += line + "\n"
            continue
        if "=" in stripped:
            blocks.append((pending_comment, line))
            pending_comment = ""
        else:
            pending_comment = ""
    return blocks


def sort_env(src: Path, dest: Path | None = None, *, reverse: bool = False) -> Path:
    """Sort keys in *src* alphabetically and write to *dest* (default: in-place)."""
    if not src.exists():
        raise SortError(f"File not found: {src}")
    dest = dest or src
    text = src.read_text()
    blocks = _parse_blocks(text)
    if not blocks:
        dest.write_text(text)
        return dest.resolve()
    blocks.sort(key=lambda b: b[1].split("=", 1)[0].strip().lower(), reverse=reverse)
    lines: list[str] = []
    for comment, kv in blocks:
        if comment:
            lines.append(comment.rstrip("\n"))
        lines.append(kv)
    dest.write_text("\n".join(lines) + "\n")
    return dest.resolve()
