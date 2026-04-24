"""Namespace support: prefix all keys with a namespace and strip it back."""
from __future__ import annotations

from pathlib import Path
from typing import List, Tuple


class NamespaceError(Exception):
    """Raised when a namespace operation fails."""


def _parse_lines(path: Path) -> List[str]:
    if not path.exists():
        raise NamespaceError(f"File not found: {path}")
    return path.read_text().splitlines(keepends=True)


def _key_of(line: str) -> str | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None
    if "=" not in stripped:
        return None
    return stripped.split("=", 1)[0].strip()


def apply_namespace(src: Path, namespace: str, dest: Path | None = None) -> Path:
    """Prefix every key in *src* with *namespace* and write to *dest*."""
    if not namespace:
        raise NamespaceError("Namespace must not be empty.")
    lines = _parse_lines(src)
    out: List[str] = []
    for line in lines:
        key = _key_of(line)
        if key and not key.startswith(namespace):
            value_part = line.split("=", 1)[1]
            out.append(f"{namespace}{key}={value_part}")
        else:
            out.append(line)
    dest = dest or src
    dest.write_text("".join(out))
    return dest.resolve()


def strip_namespace(src: Path, namespace: str, dest: Path | None = None) -> Tuple[Path, int]:
    """Remove *namespace* prefix from every matching key in *src*."""
    if not namespace:
        raise NamespaceError("Namespace must not be empty.")
    lines = _parse_lines(src)
    out: List[str] = []
    stripped_count = 0
    for line in lines:
        key = _key_of(line)
        if key and key.startswith(namespace):
            new_key = key[len(namespace):]
            value_part = line.split("=", 1)[1]
            out.append(f"{new_key}={value_part}")
            stripped_count += 1
        else:
            out.append(line)
    dest = dest or src
    dest.write_text("".join(out))
    return dest.resolve(), stripped_count
