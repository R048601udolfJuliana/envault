"""Flatten multiple .env files into a single merged output."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple


class FlattenError(Exception):
    pass


def _parse_env(text: str) -> List[Tuple[str, str]]:
    """Return ordered list of (key, raw_line) pairs, skipping comments/blanks."""
    pairs: List[Tuple[str, str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key = stripped.split("=", 1)[0].strip()
        pairs.append((key, line))
    return pairs


def flatten_env(
    sources: List[Path],
    dest: Path,
    *,
    last_wins: bool = True,
    comment_source: bool = False,
) -> Dict[str, str]:
    """Merge *sources* into *dest*.

    Args:
        sources: Ordered list of .env files to merge.
        dest: Output file path.
        last_wins: If True, later files override earlier ones for duplicate keys.
        comment_source: If True, prepend a comment indicating origin file.

    Returns:
        Mapping of key -> value written to dest.
    """
    for src in sources:
        if not src.exists():
            raise FlattenError(f"Source file not found: {src}")

    seen: Dict[str, Tuple[str, Path]] = {}  # key -> (raw_line, source)
    ordered_keys: List[str] = []

    for src in sources:
        text = src.read_text(encoding="utf-8")
        for key, raw_line in _parse_env(text):
            if key not in seen:
                ordered_keys.append(key)
            if last_wins or key not in seen:
                seen[key] = (raw_line, src)

    lines: List[str] = []
    for key in ordered_keys:
        raw_line, origin = seen[key]
        if comment_source:
            lines.append(f"# source: {origin.name}")
        lines.append(raw_line)

    dest.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    result = {}
    for key in ordered_keys:
        raw_line, _ = seen[key]
        value = raw_line.split("=", 1)[1].strip().strip('"\'')
        result[key] = value
    return result
