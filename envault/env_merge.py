"""Merge two .env files, with conflict detection and resolution strategies."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, NamedTuple, Optional


class MergeError(Exception):
    pass


class MergeConflict(NamedTuple):
    key: str
    base_value: Optional[str]
    other_value: Optional[str]

    def __str__(self) -> str:
        return f"{self.key}: base={self.base_value!r} other={self.other_value!r}"


class MergeResult(NamedTuple):
    merged: Dict[str, str]
    conflicts: List[MergeConflict]

    @property
    def has_conflicts(self) -> bool:
        return bool(self.conflicts)

    def summary_lines(self) -> List[str]:
        lines = [f"Merged keys: {len(self.merged)}"]
        if self.conflicts:
            lines.append(f"Conflicts: {len(self.conflicts)}")
            for c in self.conflicts:
                lines.append(f"  ! {c}")
        return lines


def _parse_env(text: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            result[key] = value
    return result


def merge_env(
    base_path: Path,
    other_path: Path,
    strategy: str = "ours",
) -> MergeResult:
    """Merge *other* into *base*.

    strategy:
      - 'ours'   : keep base value on conflict
      - 'theirs' : take other value on conflict
      - 'error'  : raise MergeError on first conflict
    """
    if strategy not in ("ours", "theirs", "error"):
        raise MergeError(f"Unknown strategy: {strategy!r}")
    if not base_path.exists():
        raise MergeError(f"Base file not found: {base_path}")
    if not other_path.exists():
        raise MergeError(f"Other file not found: {other_path}")

    base = _parse_env(base_path.read_text())
    other = _parse_env(other_path.read_text())

    merged: Dict[str, str] = dict(base)
    conflicts: List[MergeConflict] = []

    for key, value in other.items():
        if key not in base:
            merged[key] = value
        elif base[key] != value:
            conflict = MergeConflict(key, base[key], value)
            if strategy == "error":
                raise MergeError(f"Conflict on key: {key}")
            conflicts.append(conflict)
            if strategy == "theirs":
                merged[key] = value

    return MergeResult(merged=merged, conflicts=conflicts)


def write_merged(result: MergeResult, dest: Path) -> None:
    """Write merged key=value pairs to *dest*."""
    lines = [f"{k}={v}" for k, v in sorted(result.merged.items())]
    dest.write_text("\n".join(lines) + "\n")
