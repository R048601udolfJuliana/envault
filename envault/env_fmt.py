"""Format .env files: normalize spacing, quoting, and ordering of sections."""
from __future__ import annotations

import re
from pathlib import Path


class FmtError(Exception):
    pass


def _parse_lines(text: str) -> list[str]:
    return text.splitlines(keepends=True)


def _fmt_line(line: str, quote_values: bool = False) -> str:
    stripped = line.rstrip("\n")
    # blank or comment
    if not stripped or stripped.lstrip().startswith("#"):
        return stripped + "\n"
    if "=" not in stripped:
        return stripped + "\n"
    key, _, value = stripped.partition("=")
    key = key.strip()
    value = value.strip()
    # remove existing quotes
    if len(value) >= 2 and value[0] in ('"', "'") and value[-1] == value[0]:
        value = value[1:-1]
    if quote_values and value:
        value = f'"{value}"'
    return f"{key}={value}\n"


def format_env(src: Path, dest: Path | None = None, quote_values: bool = False) -> Path:
    """Format *src* in-place (or write to *dest*).  Return the written path."""
    if not src.exists():
        raise FmtError(f"File not found: {src}")
    lines = _parse_lines(src.read_text())
    formatted = [_fmt_line(l, quote_values=quote_values) for l in lines]
    # ensure single trailing newline
    content = "".join(formatted).rstrip("\n") + "\n"
    out = dest if dest else src
    out.write_text(content)
    return out
