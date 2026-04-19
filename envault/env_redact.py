"""Redact sensitive values in a .env file for safe display."""
from __future__ import annotations

import re
from pathlib import Path
from typing import List, Tuple

SENSITIVE_PATTERNS = re.compile(
    r"(secret|password|passwd|token|key|api|auth|credential|private|seed|salt)",
    re.IGNORECASE,
)


class RedactError(Exception):
    pass


def _parse_line(line: str) -> Tuple[str, str, str] | None:
    """Return (key, sep, value) or None if not a key=value line."""
    stripped = line.rstrip("\n")
    if stripped.startswith("#") or "=" not in stripped:
        return None
    key, _, value = stripped.partition("=")
    return key.strip(), "=", value


def redact_env(
    source: Path,
    *,
    placeholder: str = "***",
    keys: List[str] | None = None,
    auto_detect: bool = True,
) -> List[str]:
    """Return lines of the env file with sensitive values replaced.

    Args:
        source: Path to the .env file.
        placeholder: String to substitute for redacted values.
        keys: Explicit list of keys to always redact.
        auto_detect: If True, redact keys matching SENSITIVE_PATTERNS.

    Returns:
        List of redacted lines (no trailing newline per line).
    """
    if not source.exists():
        raise RedactError(f"File not found: {source}")

    explicit = {k.upper() for k in (keys or [])}
    redacted: List[str] = []

    for raw in source.read_text(encoding="utf-8").splitlines():
        parsed = _parse_line(raw)
        if parsed is None:
            redacted.append(raw)
            continue
        key, sep, value = parsed
        should_redact = key.upper() in explicit or (
            auto_detect and bool(SENSITIVE_PATTERNS.search(key))
        )
        if should_redact:
            redacted.append(f"{key}{sep}{placeholder}")
        else:
            redacted.append(raw)

    return redacted
