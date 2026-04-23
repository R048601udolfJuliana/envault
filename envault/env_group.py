"""Group .env keys by prefix into named sections."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Tuple


class GroupError(Exception):
    """Raised when grouping fails."""


def _parse_env(text: str) -> List[Tuple[str, str]]:
    """Return (key, raw_line) pairs, skipping blanks and comments."""
    result: List[Tuple[str, str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key = stripped.split("=", 1)[0].strip()
        result.append((key, line))
    return result


def group_env(
    src: Path,
    dest: Path,
    *,
    separator: str = "_",
    min_group_size: int = 1,
) -> Dict[str, List[str]]:
    """Read *src*, group keys by their first prefix segment and write *dest*.

    Returns a mapping of group_name -> list of keys in that group.
    Keys with no separator (or whose group has fewer than *min_group_size*
    members) are placed under the ``"other"`` group.
    """
    if not src.exists():
        raise GroupError(f"Source file not found: {src}")

    text = src.read_text(encoding="utf-8")
    pairs = _parse_env(text)

    groups: Dict[str, List[Tuple[str, str]]] = {}
    for key, raw in pairs:
        if separator in key:
            group = key.split(separator, 1)[0].upper()
        else:
            group = "OTHER"
        groups.setdefault(group, []).append((key, raw))

    # Merge small groups into OTHER
    final: Dict[str, List[Tuple[str, str]]] = {}
    for grp, members in groups.items():
        if grp != "OTHER" and len(members) < min_group_size:
            final.setdefault("OTHER", []).extend(members)
        else:
            final.setdefault(grp, []).extend(members)

    lines: List[str] = []
    for grp in sorted(final):
        lines.append(f"# --- {grp} ---")
        for _key, raw in final[grp]:
            lines.append(raw)
        lines.append("")

    dest.write_text("\n".join(lines), encoding="utf-8")
    return {grp: [k for k, _ in members] for grp, members in final.items()}
