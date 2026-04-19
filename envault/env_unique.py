"""Detect and remove duplicate keys from a .env file."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple


class UniqueError(Exception):
    """Raised when deduplication fails."""


@dataclass
class UniqueResult:
    duplicates: List[Tuple[str, int]] = field(default_factory=list)  # (key, line_no)
    output_lines: List[str] = field(default_factory=list)

    @property
    def has_duplicates(self) -> bool:
        return bool(self.duplicates)

    def summary_lines(self) -> List[str]:
        if not self.has_duplicates:
            return ["No duplicate keys found."]
        lines = [f"Found {len(self.duplicates)} duplicate(s):"]
        for key, lineno in self.duplicates:
            lines.append(f"  line {lineno}: {key}")
        return lines


def deduplicate_env(src: Path, dest: Path | None = None, *, keep: str = "last") -> UniqueResult:
    """Remove duplicate keys from *src*, writing result to *dest* (or in-place).

    Args:
        src:  Source .env file.
        dest: Destination path. Defaults to *src* (in-place).
        keep: ``"first"`` or ``"last"`` occurrence wins. Defaults to ``"last"``.
    """
    if not src.exists():
        raise UniqueError(f"File not found: {src}")
    if keep not in ("first", "last"):
        raise UniqueError(f"Invalid keep strategy: {keep!r}. Use 'first' or 'last'.")

    raw_lines = src.read_text(encoding="utf-8").splitlines(keepends=True)

    # Map key -> list of (index, line)
    key_indices: dict[str, list[int]] = {}
    for idx, line in enumerate(raw_lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key = stripped.split("=", 1)[0].strip()
        key_indices.setdefault(key, []).append(idx)

    duplicates: list[tuple[str, int]] = []
    remove_indices: set[int] = set()
    for key, indices in key_indices.items():
        if len(indices) < 2:
            continue
        if keep == "last":
            to_remove = indices[:-1]
        else:
            to_remove = indices[1:]
        for i in to_remove:
            duplicates.append((key, i + 1))  # 1-based line numbers
            remove_indices.add(i)

    duplicates.sort(key=lambda t: t[1])
    output_lines = [line for idx, line in enumerate(raw_lines) if idx not in remove_indices]

    dest = dest or src
    dest.write_text("".join(output_lines), encoding="utf-8")

    return UniqueResult(duplicates=duplicates, output_lines=output_lines)
