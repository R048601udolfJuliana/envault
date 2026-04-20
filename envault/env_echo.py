"""env_echo.py — Print resolved .env variables to stdout in various formats."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Tuple


class EchoError(Exception):
    """Raised when env_echo operations fail."""


_QUOTE_RE = re.compile(r'^(["\'])(.*)\1$')


def _parse_env(text: str) -> List[Tuple[str, str]]:
    """Parse env file text into ordered list of (key, value) pairs."""
    pairs: List[Tuple[str, str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        key = key.strip()
        value = value.strip()
        m = _QUOTE_RE.match(value)
        if m:
            value = m.group(2)
        pairs.append((key, value))
    return pairs


def echo_env(
    env_file: Path,
    *,
    fmt: str = "plain",
    keys: List[str] | None = None,
    mask: bool = False,
) -> List[str]:
    """Return lines representing env variables in the requested format.

    Args:
        env_file: Path to the .env file.
        fmt: Output format — 'plain', 'export', or 'json'.
        keys: If provided, only include these keys.
        mask: Replace values with '***' for sensitive display.

    Returns:
        A list of formatted strings.

    Raises:
        EchoError: If the file is missing or the format is unknown.
    """
    if not env_file.exists():
        raise EchoError(f"env file not found: {env_file}")
    if fmt not in ("plain", "export", "json"):
        raise EchoError(f"unknown format '{fmt}'; choose plain, export, or json")

    text = env_file.read_text(encoding="utf-8")
    pairs = _parse_env(text)

    if keys:
        key_set = set(keys)
        pairs = [(k, v) for k, v in pairs if k in key_set]

    if mask:
        pairs = [(k, "***") for k, v in pairs]

    if fmt == "plain":
        return [f"{k}={v}" for k, v in pairs]
    elif fmt == "export":
        return [f"export {k}={v}" for k, v in pairs]
    else:  # json
        import json
        d: Dict[str, str] = {k: v for k, v in pairs}
        return [json.dumps(d, indent=2)]
