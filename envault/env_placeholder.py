"""Detect and report unresolved placeholder values in .env files.

A placeholder is a value matching patterns like <VALUE>, ${VAR}, {{KEY}},
or CHANGEME / TODO (case-insensitive).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

_PLACEHOLDER_RE = re.compile(
    r'^(<[^>]+>|\$\{[^}]+\}|\{\{[^}]+\}\}|changeme|todo|fixme|placeholder|replace_me)$',
    re.IGNORECASE,
)


class PlaceholderError(Exception):
    """Raised on I/O or parse failures."""


@dataclass
class PlaceholderMatch:
    key: str
    value: str
    line_no: int

    def __str__(self) -> str:
        return f"line {self.line_no}: {self.key}={self.value}"


@dataclass
class PlaceholderResult:
    matches: List[PlaceholderMatch] = field(default_factory=list)

    @property
    def found(self) -> bool:
        return bool(self.matches)

    def summary_lines(self) -> List[str]:
        if not self.matches:
            return ["No placeholder values detected."]
        lines = [f"Found {len(self.matches)} placeholder(s):"]
        for m in self.matches:
            lines.append(f"  {m}")
        return lines


def _strip_quotes(value: str) -> str:
    for q in ('"', "'"):
        if value.startswith(q) and value.endswith(q) and len(value) >= 2:
            return value[1:-1]
    return value


def scan_placeholders(src: Path) -> PlaceholderResult:
    """Scan *src* for lines whose values look like unresolved placeholders."""
    if not src.exists():
        raise PlaceholderError(f"File not found: {src}")
    try:
        text = src.read_text(encoding="utf-8")
    except OSError as exc:
        raise PlaceholderError(str(exc)) from exc

    result = PlaceholderResult()
    for lineno, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        value = _strip_quotes(value.strip())
        if _PLACEHOLDER_RE.match(value):
            result.matches.append(PlaceholderMatch(key.strip(), value, lineno))
    return result
