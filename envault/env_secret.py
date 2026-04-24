"""Detect and report secrets/high-entropy values in .env files."""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


class SecretError(Exception):
    """Raised when secret detection fails."""


_SENSITIVE_PATTERNS = re.compile(
    r"(password|passwd|secret|token|api[_-]?key|auth|private[_-]?key|credentials)",
    re.IGNORECASE,
)

_MIN_ENTROPY = 3.5
_MIN_VALUE_LEN = 8


@dataclass
class SecretMatch:
    key: str
    value: str
    reason: str

    def __str__(self) -> str:
        masked = self.value[:2] + "***" if len(self.value) > 2 else "***"
        return f"{self.key}={masked}  ({self.reason})"


@dataclass
class SecretResult:
    matches: List[SecretMatch] = field(default_factory=list)

    @property
    def found(self) -> bool:
        return bool(self.matches)

    def summary_lines(self) -> List[str]:
        if not self.matches:
            return ["No secrets detected."]
        lines = [f"Detected {len(self.matches)} potential secret(s):"]
        lines.extend(f"  {m}" for m in self.matches)
        return lines


def _entropy(value: str) -> float:
    if not value:
        return 0.0
    freq = {c: value.count(c) / len(value) for c in set(value)}
    return -sum(p * math.log2(p) for p in freq.values())


def _parse_env(text: str) -> List[tuple]:
    pairs = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, val = stripped.partition("=")
        val = val.strip().strip('"').strip("'")
        pairs.append((key.strip(), val))
    return pairs


def scan_secrets(
    env_path: Path,
    check_entropy: bool = True,
    check_names: bool = True,
) -> SecretResult:
    """Scan an env file for potential secrets."""
    if not env_path.exists():
        raise SecretError(f"File not found: {env_path}")
    pairs = _parse_env(env_path.read_text())
    matches: List[SecretMatch] = []
    for key, value in pairs:
        if not value:
            continue
        if check_names and _SENSITIVE_PATTERNS.search(key):
            matches.append(SecretMatch(key, value, "sensitive key name"))
            continue
        if check_entropy and len(value) >= _MIN_VALUE_LEN:
            ent = _entropy(value)
            if ent >= _MIN_ENTROPY:
                matches.append(SecretMatch(key, value, f"high entropy ({ent:.2f})"))
    return SecretResult(matches=matches)
