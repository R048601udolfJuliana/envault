"""Show the first N keys from a .env file."""
from __future__ import annotations

from pathlib import Path
from typing import List, Tuple


class HeadError(Exception):
    pass


def _parse_env(text: str) -> List[Tuple[str, str]]:
    pairs: List[Tuple[str, str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        value = value.strip().strip('"').strip("'")
        pairs.append((key.strip(), value))
    return pairs


def head_env(path: Path, n: int = 10) -> List[Tuple[str, str]]:
    """Return the first *n* key/value pairs from *path*."""
    if n < 1:
        raise HeadError(f"n must be >= 1, got {n}")
    if not path.exists():
        raise HeadError(f"File not found: {path}")
    text = path.read_text(encoding="utf-8")
    pairs = _parse_env(text)
    return pairs[:n]
