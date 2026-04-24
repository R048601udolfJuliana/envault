"""Tokenize .env file values into typed tokens for inspection."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


class TokenizeError(Exception):
    """Raised when tokenization fails."""


TOKEN_TYPES = ("url", "path", "integer", "float", "boolean", "uuid", "email", "string")

_URL_RE = re.compile(r'^https?://', re.IGNORECASE)
_PATH_RE = re.compile(r'^[./~]')
_UUID_RE = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
_EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
_BOOL_VALUES = {"true", "false", "yes", "no", "1", "0"}


@dataclass
class TokenizedEntry:
    key: str
    raw_value: str
    token_type: str

    def __str__(self) -> str:
        return f"{self.key}={self.raw_value!r}  [{self.token_type}]"


@dataclass
class TokenizeResult:
    entries: List[TokenizedEntry] = field(default_factory=list)

    def by_type(self, token_type: str) -> List[TokenizedEntry]:
        return [e for e in self.entries if e.token_type == token_type]

    def summary_lines(self) -> List[str]:
        from collections import Counter
        counts = Counter(e.token_type for e in self.entries)
        lines = [f"Total keys: {len(self.entries)}"]
        for t in TOKEN_TYPES:
            if counts[t]:
                lines.append(f"  {t}: {counts[t]}")
        return lines


def _detect_type(value: str) -> str:
    v = value.strip().strip('"\'')
    if _URL_RE.match(v):
        return "url"
    if _EMAIL_RE.match(v):
        return "email"
    if _UUID_RE.match(v):
        return "uuid"
    if v.lower() in _BOOL_VALUES:
        return "boolean"
    try:
        int(v)
        return "integer"
    except ValueError:
        pass
    try:
        float(v)
        return "float"
    except ValueError:
        pass
    if _PATH_RE.match(v):
        return "path"
    return "string"


def _parse_env(text: str) -> List[tuple]:
    pairs = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        pairs.append((key.strip(), value.strip()))
    return pairs


def tokenize_env(src: Path) -> TokenizeResult:
    """Parse *src* and classify each value into a token type."""
    if not src.exists():
        raise TokenizeError(f"File not found: {src}")
    text = src.read_text(encoding="utf-8")
    pairs = _parse_env(text)
    entries = [TokenizedEntry(key=k, raw_value=v, token_type=_detect_type(v)) for k, v in pairs]
    return TokenizeResult(entries=entries)
