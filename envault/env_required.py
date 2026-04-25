"""Check that required keys are present and non-empty in a .env file."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


class RequiredError(Exception):
    """Raised when required-key checking fails unexpectedly."""


@dataclass
class MissingKey:
    key: str
    reason: str  # 'absent' | 'empty'

    def __str__(self) -> str:
        return f"{self.key}: {self.reason}"


@dataclass
class RequiredResult:
    missing: List[MissingKey] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.missing) == 0

    def summary_lines(self) -> List[str]:
        if self.ok:
            return ["All required keys are present."]
        return [f"  - {m}" for m in self.missing]


def _parse_env(text: str) -> dict:
    env: dict = {}
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
            env[key] = value
    return env


def check_required(
    env_path: Path,
    required_keys: List[str],
    allow_empty: bool = False,
) -> RequiredResult:
    """Return a RequiredResult indicating which required keys are missing or empty."""
    if not env_path.exists():
        raise RequiredError(f"env file not found: {env_path}")
    if not required_keys:
        return RequiredResult()

    try:
        text = env_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RequiredError(str(exc)) from exc

    env = _parse_env(text)
    result = RequiredResult()

    for key in required_keys:
        if key not in env:
            result.missing.append(MissingKey(key=key, reason="absent"))
        elif not allow_empty and env[key] == "":
            result.missing.append(MissingKey(key=key, reason="empty"))

    return result
