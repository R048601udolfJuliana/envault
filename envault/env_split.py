"""Split a .env file into multiple files by key prefix."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Tuple


class SplitError(Exception):
    pass


def _parse_blocks(text: str) -> List[Tuple[str, str]]:
    """Return list of (key, raw_line) for non-comment, non-blank lines."""
    result = []
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)\s*=', stripped)
        if m:
            result.append((m.group(1), line))
    return result


def split_env(
    src: Path,
    dest_dir: Path,
    prefixes: List[str],
    default_file: str = ".env.other",
) -> Dict[str, Path]:
    """Split *src* into per-prefix files inside *dest_dir*.

    Keys matching ``PREFIX_*`` go to ``<dest_dir>/.env.<prefix_lower>``.
    Unmatched keys go to *default_file*.

    Returns a mapping of output filename -> Path.
    """
    if not src.exists():
        raise SplitError(f"Source file not found: {src}")

    dest_dir.mkdir(parents=True, exist_ok=True)
    text = src.read_text()
    buckets: Dict[str, List[str]] = {p.upper(): [] for p in prefixes}
    buckets["__default__"] = []

    for key, line in _parse_blocks(text):
        matched = False
        for prefix in prefixes:
            if key.upper().startswith(prefix.upper() + "_") or key.upper() == prefix.upper():
                buckets[prefix.upper()].append(line)
                matched = True
                break
        if not matched:
            buckets["__default__"].append(line)

    written: Dict[str, Path] = {}
    for prefix in prefixes:
        lines = buckets[prefix.upper()]
        if lines:
            out = dest_dir / f".env.{prefix.lower()}"
            out.write_text("".join(lines))
            written[out.name] = out

    default_lines = buckets["__default__"]
    if default_lines:
        out = dest_dir / default_file
        out.write_text("".join(default_lines))
        written[out.name] = out

    return written
