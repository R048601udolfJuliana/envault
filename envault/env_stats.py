"""Statistics and summary metrics for .env files."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


class StatsError(Exception):
    pass


@dataclass
class EnvStats:
    total_keys: int = 0
    empty_values: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    longest_key: str = ""
    longest_value_key: str = ""
    duplicate_keys: list[str] = field(default_factory=list)

    def summary_lines(self) -> list[str]:
        lines = [
            f"Total keys      : {self.total_keys}",
            f"Empty values    : {self.empty_values}",
            f"Comment lines   : {self.comment_lines}",
            f"Blank lines     : {self.blank_lines}",
            f"Longest key     : {self.longest_key or '(none)'}",
            f"Longest value   : {self.longest_value_key or '(none)'}",
        ]
        if self.duplicate_keys:
            lines.append(f"Duplicate keys  : {', '.join(self.duplicate_keys)}")
        return lines


def compute_stats(path: Path) -> EnvStats:
    if not path.exists():
        raise StatsError(f"File not found: {path}")

    text = path.read_text(encoding="utf-8")
    stats = EnvStats()
    seen: dict[str, int] = {}
    longest_val_len = 0

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            stats.blank_lines += 1
            continue
        if line.startswith("#"):
            stats.comment_lines += 1
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = re.sub(r'^(["\'])(.*)\1$', r"\2", value.strip())
        stats.total_keys += 1
        if not value:
            stats.empty_values += 1
        if not stats.longest_key or len(key) > len(stats.longest_key):
            stats.longest_key = key
        if len(value) > longest_val_len:
            longest_val_len = len(value)
            stats.longest_value_key = key
        seen[key] = seen.get(key, 0) + 1

    stats.duplicate_keys = [k for k, c in seen.items() if c > 1]
    return stats
