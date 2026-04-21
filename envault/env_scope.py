"""Scope filtering: keep or drop keys by environment scope (e.g. dev/prod/test)."""
from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional


class ScopeError(Exception):
    """Raised when a scoping operation fails."""


# Keys are considered to belong to a scope when they start with <SCOPE>_  (case-insensitive)
_SCOPE_RE = re.compile(r'^([A-Za-z0-9]+)_(.+)$')


def _parse_lines(text: str) -> List[str]:
    return text.splitlines(keepends=True)


def _key_of(line: str) -> Optional[str]:
    stripped = line.strip()
    if not stripped or stripped.startswith('#'):
        return None
    if '=' not in stripped:
        return None
    return stripped.split('=', 1)[0].strip()


def scope_env(
    src: Path,
    scope: str,
    *,
    dest: Optional[Path] = None,
    strip_prefix: bool = False,
    keep_unscoped: bool = True,
) -> Path:
    """Filter *src* to lines that belong to *scope*.

    A line belongs to *scope* when its key matches ``<SCOPE>_*`` (case-insensitive).
    Lines with no scope prefix are kept when *keep_unscoped* is True.

    If *strip_prefix* is True the ``<SCOPE>_`` prefix is removed from matching keys.
    """
    if not src.exists():
        raise ScopeError(f"Source file not found: {src}")
    if not scope:
        raise ScopeError("Scope must be a non-empty string.")

    scope_upper = scope.upper()
    lines = _parse_lines(src.read_text(encoding="utf-8"))
    out: List[str] = []

    for line in lines:
        raw = line.rstrip("\n")
        key = _key_of(raw)
        if key is None:
            # comment or blank – always keep
            out.append(line)
            continue
        m = _SCOPE_RE.match(key)
        if m and m.group(1).upper() == scope_upper:
            if strip_prefix:
                suffix = m.group(2)
                value_part = raw.split('=', 1)[1]
                line = suffix + '=' + value_part + '\n'
            out.append(line)
        elif not m and keep_unscoped:
            out.append(line)
        # else: scoped to a different scope – drop

    if dest is None:
        dest = src.parent / f".env.{scope.lower()}"
    dest.write_text(''.join(out), encoding="utf-8")
    return dest.resolve()
