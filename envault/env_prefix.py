"""Add or strip a prefix from all keys in a .env file."""
from __future__ import annotations

from pathlib import Path
from typing import List, Tuple


class PrefixError(Exception):
    """Raised when a prefix operation fails."""


def _parse_lines(text: str) -> List[Tuple[str, str]]:
    """Return list of (raw_line, key_or_empty) tuples."""
    result = []
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            result.append((line, ""))
            continue
        if "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            result.append((line, key))
        else:
            result.append((line, ""))
    return result


def add_prefix(src: Path, prefix: str, dest: Path | None = None) -> Path:
    """Prepend *prefix* to every key in *src* and write to *dest*."""
    if not prefix:
        raise PrefixError("prefix must not be empty")
    if not src.exists():
        raise PrefixError(f"source file not found: {src}")

    out_path = dest or src
    lines = _parse_lines(src.read_text(encoding="utf-8"))
    out: List[str] = []
    for raw, key in lines:
        if key and not key.startswith(prefix):
            value_part = raw.split("=", 1)[1]
            out.append(f"{prefix}{key}={value_part}")
        else:
            out.append(raw)
    out_path.write_text("".join(out), encoding="utf-8")
    return out_path


def strip_prefix(src: Path, prefix: str, dest: Path | None = None) -> Path:
    """Remove *prefix* from every matching key in *src* and write to *dest*."""
    if not prefix:
        raise PrefixError("prefix must not be empty")
    if not src.exists():
        raise PrefixError(f"source file not found: {src}")

    out_path = dest or src
    lines = _parse_lines(src.read_text(encoding="utf-8"))
    out: List[str] = []
    for raw, key in lines:
        if key and key.startswith(prefix):
            new_key = key[len(prefix):]
            value_part = raw.split("=", 1)[1]
            out.append(f"{new_key}={value_part}")
        else:
            out.append(raw)
    out_path.write_text("".join(out), encoding="utf-8")
    return out_path
