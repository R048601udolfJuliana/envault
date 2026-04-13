"""Diff utilities for comparing plaintext .env files."""
from __future__ import annotations

import difflib
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple


class DiffError(Exception):
    """Raised when a diff operation fails."""


@dataclass
class EnvDiff:
    """Result of comparing two .env files."""

    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    changed: List[Tuple[str, str, str]] = field(default_factory=list)  # (key, old, new)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    def summary(self) -> str:
        lines = []
        for key in self.added:
            lines.append(f"+ {key}")
        for key in self.removed:
            lines.append(f"- {key}")
        for key, old, new in self.changed:
            lines.append(f"~ {key}: {old!r} -> {new!r}")
        return "\n".join(lines) if lines else "No changes."


def _parse_env(text: str) -> dict[str, str]:
    """Parse key=value pairs from .env text, ignoring comments and blanks."""
    result: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        result[key.strip()] = value.strip()
    return result


def diff_env_files(old_path: Path, new_path: Path) -> EnvDiff:
    """Compare two .env files and return an EnvDiff."""
    for p in (old_path, new_path):
        if not p.exists():
            raise DiffError(f"File not found: {p}")

    old_vars = _parse_env(old_path.read_text())
    new_vars = _parse_env(new_path.read_text())

    old_keys = set(old_vars)
    new_keys = set(new_vars)

    added = sorted(new_keys - old_keys)
    removed = sorted(old_keys - new_keys)
    changed = [
        (k, old_vars[k], new_vars[k])
        for k in sorted(old_keys & new_keys)
        if old_vars[k] != new_vars[k]
    ]
    return EnvDiff(added=added, removed=removed, changed=changed)


def unified_diff(old_path: Path, new_path: Path) -> str:
    """Return a unified diff string between two .env files."""
    for p in (old_path, new_path):
        if not p.exists():
            raise DiffError(f"File not found: {p}")

    old_lines = old_path.read_text().splitlines(keepends=True)
    new_lines = new_path.read_text().splitlines(keepends=True)
    return "".join(
        difflib.unified_diff(
            old_lines, new_lines,
            fromfile=str(old_path),
            tofile=str(new_path),
        )
    )
