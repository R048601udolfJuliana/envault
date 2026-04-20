"""Base64 encoding/decoding of .env file values."""
from __future__ import annotations

import base64
import re
from pathlib import Path
from typing import List, Tuple


class EncodeError(Exception):
    """Raised when encoding/decoding fails."""


# KEY=VALUE  (optional inline comment stripped before processing)
_LINE_RE = re.compile(r'^([A-Za-z_][A-Za-z0-9_]*)=(.*)')


def _parse_lines(text: str) -> List[Tuple[str, str, str]]:
    """Return list of (key, value, raw_line) tuples."""
    result = []
    for line in text.splitlines(keepends=True):
        m = _LINE_RE.match(line)
        if m:
            result.append((m.group(1), m.group(2).rstrip('\n'), line))
        else:
            result.append(('', '', line))
    return result


def encode_env(
    src: Path,
    dest: Path | None = None,
    *,
    keys: List[str] | None = None,
) -> Path:
    """Base64-encode values in *src* and write to *dest* (default: src)."""
    if not src.exists():
        raise EncodeError(f"File not found: {src}")
    parsed = _parse_lines(src.read_text())
    out_lines: List[str] = []
    for key, value, raw in parsed:
        if key and (keys is None or key in keys):
            stripped = value.strip('"\'')
            encoded = base64.b64encode(stripped.encode()).decode()
            out_lines.append(f"{key}={encoded}\n")
        else:
            out_lines.append(raw if raw.endswith('\n') else raw + '\n')
    target = dest or src
    target.write_text(''.join(out_lines))
    return target.resolve()


def decode_env(
    src: Path,
    dest: Path | None = None,
    *,
    keys: List[str] | None = None,
) -> Path:
    """Base64-decode values in *src* and write to *dest* (default: src)."""
    if not src.exists():
        raise EncodeError(f"File not found: {src}")
    parsed = _parse_lines(src.read_text())
    out_lines: List[str] = []
    for key, value, raw in parsed:
        if key and (keys is None or key in keys):
            try:
                decoded = base64.b64decode(value.encode()).decode()
            except Exception as exc:
                raise EncodeError(
                    f"Cannot base64-decode value for key '{key}': {exc}"
                ) from exc
            out_lines.append(f"{key}={decoded}\n")
        else:
            out_lines.append(raw if raw.endswith('\n') else raw + '\n')
    target = dest or src
    target.write_text(''.join(out_lines))
    return target.resolve()
