"""Count keys in a .env file, optionally filtered by pattern."""
from __future__ import annotations

import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


class CountError(Exception):
    pass


@dataclass
class CountResult:
    total: int
    empty: int
    non_empty: int
    pattern: Optional[str] = None
    matched: int = 0

    def summary_lines(self) -> list[str]:
        lines = [
            f"Total keys   : {self.total}",
            f"Non-empty    : {self.non_empty}",
            f"Empty values : {self.empty}",
        ]
        if self.pattern is not None:
            lines.append(f"Matched '{self.pattern}': {self.matched}")
        return lines


def _parse_env(text: str) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            pairs.append((key, value))
    return pairs


def count_keys(
    env_path: Path,
    pattern: Optional[str] = None,
    case_sensitive: bool = False,
) -> CountResult:
    """Count keys in *env_path*, optionally filtering by *pattern* (regex)."""
    if not env_path.exists():
        raise CountError(f"File not found: {env_path}")
    try:
        text = env_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise CountError(str(exc)) from exc

    pairs = _parse_env(text)
    total = len(pairs)
    empty = sum(1 for _, v in pairs if not v)
    non_empty = total - empty

    matched = 0
    if pattern is not None:
        flags = 0 if case_sensitive else re.IGNORECASE
        try:
            rx = re.compile(pattern, flags)
        except re.error as exc:
            raise CountError(f"Invalid pattern: {exc}") from exc
        matched = sum(1 for k, _ in pairs if rx.search(k))

    return CountResult(
        total=total,
        empty=empty,
        non_empty=non_empty,
        pattern=pattern,
        matched=matched,
    )
