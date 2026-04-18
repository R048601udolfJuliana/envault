"""Search for keys or values matching a pattern in a .env file."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


class GrepError(Exception):
    pass


@dataclass
class GrepMatch:
    line_no: int
    key: str
    value: str
    matched_field: str  # 'key' | 'value' | 'both'

    def __str__(self) -> str:
        return f"  [{self.line_no:3d}] {self.key}={self.value}  (matched: {self.matched_field})"


@dataclass
class GrepResult:
    matches: List[GrepMatch] = field(default_factory=list)

    @property
    def found(self) -> bool:
        return bool(self.matches)

    def summary(self) -> str:
        if not self.found:
            return "No matches found."
        lines = [f"{len(self.matches)} match(es):"]
        lines.extend(str(m) for m in self.matches)
        return "\n".join(lines)


def _parse_env(text: str):
    pairs = []
    for i, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        pairs.append((i, key, value))
    return pairs


def grep_env(
    env_file: Path,
    pattern: str,
    *,
    search_values: bool = True,
    search_keys: bool = True,
    case_sensitive: bool = False,
) -> GrepResult:
    """Return all key/value pairs matching *pattern*."""
    env_file = Path(env_file)
    if not env_file.exists():
        raise GrepError(f"File not found: {env_file}")
    if not search_keys and not search_values:
        raise GrepError("At least one of search_keys or search_values must be True.")

    flags = 0 if case_sensitive else re.IGNORECASE
    try:
        rx = re.compile(pattern, flags)
    except re.error as exc:
        raise GrepError(f"Invalid pattern: {exc}") from exc

    text = env_file.read_text(encoding="utf-8")
    result = GrepResult()
    for line_no, key, value in _parse_env(text):
        hit_key = search_keys and bool(rx.search(key))
        hit_val = search_values and bool(rx.search(value))
        if hit_key or hit_val:
            matched = "both" if (hit_key and hit_val) else ("key" if hit_key else "value")
            result.matches.append(GrepMatch(line_no, key, value, matched))
    return result
