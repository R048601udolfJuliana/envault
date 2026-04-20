"""Add, remove, or list inline comments on .env keys."""
from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional, Tuple


class CommentError(Exception):
    """Raised when a comment operation fails."""


# Matches:  KEY=value  # optional existing comment
_LINE_RE = re.compile(r'^([A-Za-z_][A-Za-z0-9_]*)\s*=(.*)$')
_COMMENT_RE = re.compile(r'^(.*?)\s*#\s*(.*)$')


def _parse_lines(text: str) -> List[Tuple[str, str, Optional[str]]]:
    """Return list of (raw_line, kind, key) where kind is 'kv'/'comment'/'blank'."""
    result = []
    for line in text.splitlines(keepends=True):
        stripped = line.rstrip('\n').rstrip('\r')
        if not stripped or stripped.lstrip().startswith('#'):
            result.append((line, 'other', None))
        else:
            m = _LINE_RE.match(stripped)
            if m:
                result.append((line, 'kv', m.group(1)))
            else:
                result.append((line, 'other', None))
    return result


def set_comment(path: Path, key: str, comment: str) -> None:
    """Add or replace the inline comment for *key* in the env file."""
    if not path.exists():
        raise CommentError(f"File not found: {path}")
    if not comment:
        raise CommentError("Comment must not be empty; use remove_comment to delete.")

    text = path.read_text(encoding='utf-8')
    lines = _parse_lines(text)
    found = False
    out = []
    for raw, kind, k in lines:
        if kind == 'kv' and k == key:
            stripped = raw.rstrip('\n').rstrip('\r')
            # Strip existing inline comment
            m = _COMMENT_RE.match(stripped)
            base = m.group(1).rstrip() if m else stripped
            out.append(f"{base}  # {comment}\n")
            found = True
        else:
            out.append(raw)
    if not found:
        raise CommentError(f"Key '{key}' not found in {path}")
    path.write_text(''.join(out), encoding='utf-8')


def remove_comment(path: Path, key: str) -> None:
    """Remove the inline comment from *key*, leaving the value intact."""
    if not path.exists():
        raise CommentError(f"File not found: {path}")
    text = path.read_text(encoding='utf-8')
    lines = _parse_lines(text)
    found = False
    out = []
    for raw, kind, k in lines:
        if kind == 'kv' and k == key:
            stripped = raw.rstrip('\n').rstrip('\r')
            m = _COMMENT_RE.match(stripped)
            base = m.group(1).rstrip() if m else stripped
            out.append(f"{base}\n")
            found = True
        else:
            out.append(raw)
    if not found:
        raise CommentError(f"Key '{key}' not found in {path}")
    path.write_text(''.join(out), encoding='utf-8')


def list_comments(path: Path) -> List[Tuple[str, str]]:
    """Return [(key, comment), ...] for every key that has an inline comment."""
    if not path.exists():
        raise CommentError(f"File not found: {path}")
    text = path.read_text(encoding='utf-8')
    result = []
    for raw, kind, key in _parse_lines(text):
        if kind == 'kv':
            stripped = raw.rstrip('\n').rstrip('\r')
            m = _COMMENT_RE.match(stripped)
            if m:
                result.append((key, m.group(2).strip()))
    return result
