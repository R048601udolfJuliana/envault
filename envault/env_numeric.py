"""Numeric analysis for .env files — identify and validate numeric values."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


class NumericError(Exception):
    """Raised when numeric analysis fails."""


@dataclass
class NumericResult:
    integers: Dict[str, int] = field(default_factory=dict)
    floats: Dict[str, float] = field(default_factory=dict)
    non_numeric: List[str] = field(default_factory=list)

    def summary_lines(self) -> List[str]:
        lines = []
        lines.append(f"Integers : {len(self.integers)}")
        lines.append(f"Floats   : {len(self.floats)}")
        lines.append(f"Other    : {len(self.non_numeric)}")
        return lines


def _parse_env(text: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            result[key] = value
    return result


def _try_parse(value: str) -> Optional[object]:
    """Return int, float, or None."""
    try:
        int_val = int(value)
        return int_val
    except ValueError:
        pass
    try:
        float_val = float(value)
        return float_val
    except ValueError:
        pass
    return None


def analyze_numeric(path: Path) -> NumericResult:
    """Parse *path* and classify each key's value as int, float, or other."""
    if not path.exists():
        raise NumericError(f"File not found: {path}")
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise NumericError(str(exc)) from exc

    pairs = _parse_env(text)
    result = NumericResult()
    for key, value in pairs.items():
        parsed = _try_parse(value)
        if parsed is None:
            result.non_numeric.append(key)
        elif isinstance(parsed, int):
            result.integers[key] = parsed
        else:
            result.floats[key] = parsed
    return result
