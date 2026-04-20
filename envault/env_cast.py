"""env_cast.py — cast .env values to typed Python representations."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Tuple


class CastError(Exception):
    """Raised when casting fails."""


_BOOL_TRUE = {"true", "yes", "1", "on"}
_BOOL_FALSE = {"false", "no", "0", "off"}


def _parse_env(text: str) -> List[Tuple[str, str]]:
    """Return (key, raw_value) pairs, skipping comments and blanks."""
    pairs: List[Tuple[str, str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, val = stripped.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key:
            pairs.append((key, val))
    return pairs


def _cast_value(raw: str, hint: str) -> Any:
    """Cast *raw* string to the type indicated by *hint*."""
    hint = hint.lower()
    if hint == "int":
        try:
            return int(raw)
        except ValueError:
            raise CastError(f"Cannot cast {raw!r} to int")
    if hint == "float":
        try:
            return float(raw)
        except ValueError:
            raise CastError(f"Cannot cast {raw!r} to float")
    if hint == "bool":
        if raw.lower() in _BOOL_TRUE:
            return True
        if raw.lower() in _BOOL_FALSE:
            return False
        raise CastError(f"Cannot cast {raw!r} to bool")
    if hint == "list":
        return [item.strip() for item in raw.split(",") if item.strip()]
    if hint == "str":
        return raw
    raise CastError(f"Unknown type hint: {hint!r}")


def cast_env(
    src: Path,
    hints: Dict[str, str],
) -> Dict[str, Any]:
    """Parse *src* and cast values according to *hints* mapping key→type.

    Keys not present in *hints* are returned as plain strings.
    """
    if not src.exists():
        raise CastError(f"File not found: {src}")
    text = src.read_text(encoding="utf-8")
    pairs = _parse_env(text)
    result: Dict[str, Any] = {}
    for key, raw in pairs:
        hint = hints.get(key, "str")
        result[key] = _cast_value(raw, hint)
    return result
