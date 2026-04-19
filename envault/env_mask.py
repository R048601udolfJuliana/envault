"""Mask sensitive values in .env files for safe display."""
from __future__ import annotations

import re
from pathlib import Path

SENSITIVE_PATTERNS = re.compile(
    r"(secret|password|passwd|token|key|api|auth|private|credential)",
    re.IGNORECASE,
)

DEFAULT_PLACEHOLDER = "***"


class MaskError(Exception):
    pass


def _parse_line(line: str) -> tuple[str, str] | None:
    """Return (key, value) if line is a key=value pair, else None."""
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None
    if "=" not in stripped:
        return None
    key, _, value = stripped.partition("=")
    return key.strip(), value.strip().strip('"').strip("'")


def mask_env(
    source: Path,
    dest: Path | None = None,
    *,
    keys: list[str] | None = None,
    placeholder: str = DEFAULT_PLACEHOLDER,
    auto_detect: bool = True,
) -> dict[str, str]:
    """Mask sensitive values and return a dict of masked key->original_value.

    If *dest* is given the masked content is written there; otherwise the
    masked lines are only returned as a mapping.
    """
    if not source.exists():
        raise MaskError(f"Source file not found: {source}")

    lines = source.read_text().splitlines(keepends=True)
    masked: dict[str, str] = {}
    out_lines: list[str] = []

    explicit = set(keys or [])

    for line in lines:
        parsed = _parse_line(line)
        if parsed is None:
            out_lines.append(line)
            continue

        key, value = parsed
        should_mask = key in explicit or (auto_detect and SENSITIVE_PATTERNS.search(key))

        if should_mask and value:
            masked[key] = value
            out_lines.append(f"{key}={placeholder}\n")
        else:
            out_lines.append(line)

    if dest is not None:
        dest.write_text("".join(out_lines))

    return masked
