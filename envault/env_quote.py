"""env_quote.py — quote or unquote values in a .env file."""
from __future__ import annotations

from pathlib import Path
from typing import List, Tuple


class QuoteError(Exception):
    """Raised when quoting/unquoting fails."""


QuoteStyle = str  # 'double', 'single', or 'none'


def _parse_lines(text: str) -> List[Tuple[str, str, str]]:
    """Return list of (key, value, raw_line) for each line."""
    result = []
    for line in text.splitlines(keepends=True):
        stripped = line.rstrip("\n")
        if not stripped or stripped.lstrip().startswith("#") or "=" not in stripped:
            result.append(("", "", line))
            continue
        key, _, val = stripped.partition("=")
        result.append((key, val, line))
    return result


def _strip_quotes(value: str) -> str:
    """Remove surrounding single or double quotes from a value."""
    if len(value) >= 2:
        if (value[0] == '"' and value[-1] == '"') or (
            value[0] == "'" and value[-1] == "'"
        ):
            return value[1:-1]
    return value


def _apply_quote(value: str, style: QuoteStyle) -> str:
    bare = _strip_quotes(value)
    if style == "double":
        return f'"{bare}"'
    if style == "single":
        return f"'{bare}'"
    return bare  # 'none'


def quote_env(
    src: Path,
    dest: Path | None = None,
    style: QuoteStyle = "double",
    keys: list[str] | None = None,
) -> Path:
    """Re-quote values in *src* using *style* and write to *dest*.

    Args:
        src:   Source .env file.
        dest:  Destination path; defaults to *src* (in-place).
        style: One of ``'double'``, ``'single'``, or ``'none'``.
        keys:  Restrict operation to these keys; ``None`` means all.

    Returns:
        Resolved destination path.
    """
    if style not in ("double", "single", "none"):
        raise QuoteError(f"Unknown quote style: {style!r}. Use 'double', 'single', or 'none'.")

    src = Path(src)
    if not src.exists():
        raise QuoteError(f"Source file not found: {src}")

    dest = Path(dest) if dest else src
    text = src.read_text(encoding="utf-8")
    out_lines: list[str] = []

    for key, val, raw in _parse_lines(text):
        if not key:
            out_lines.append(raw)
            continue
        if keys is None or key in keys:
            new_val = _apply_quote(val, style)
            eol = "\n" if raw.endswith("\n") else ""
            out_lines.append(f"{key}={new_val}{eol}")
        else:
            out_lines.append(raw)

    dest.write_text("".join(out_lines), encoding="utf-8")
    return dest.resolve()
