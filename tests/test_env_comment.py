"""Tests for envault.env_comment."""
from __future__ import annotations

import pytest
from pathlib import Path

from envault.env_comment import (
    CommentError,
    list_comments,
    remove_comment,
    set_comment,
)


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content, encoding='utf-8')
    return p


def test_set_comment_adds_new_comment(tmp_dir: Path) -> None:
    f = _write(tmp_dir / '.env', 'API_KEY=secret\nDEBUG=true\n')
    set_comment(f, 'API_KEY', 'rotate monthly')
    text = f.read_text()
    assert 'API_KEY=secret  # rotate monthly' in text
    assert 'DEBUG=true' in text


def test_set_comment_replaces_existing_comment(tmp_dir: Path) -> None:
    f = _write(tmp_dir / '.env', 'API_KEY=secret  # old comment\n')
    set_comment(f, 'API_KEY', 'new comment')
    text = f.read_text()
    assert '# new comment' in text
    assert 'old comment' not in text


def test_set_comment_missing_file_raises(tmp_dir: Path) -> None:
    with pytest.raises(CommentError, match='not found'):
        set_comment(tmp_dir / 'missing.env', 'KEY', 'hi')


def test_set_comment_empty_comment_raises(tmp_dir: Path) -> None:
    f = _write(tmp_dir / '.env', 'KEY=val\n')
    with pytest.raises(CommentError, match='empty'):
        set_comment(f, 'KEY', '')


def test_set_comment_missing_key_raises(tmp_dir: Path) -> None:
    f = _write(tmp_dir / '.env', 'OTHER=val\n')
    with pytest.raises(CommentError, match="'MISSING'"):
        set_comment(f, 'MISSING', 'note')


def test_remove_comment_strips_inline_comment(tmp_dir: Path) -> None:
    f = _write(tmp_dir / '.env', 'DB_URL=postgres://localhost  # internal\n')
    remove_comment(f, 'DB_URL')
    text = f.read_text()
    assert 'DB_URL=postgres://localhost' in text
    assert '# internal' not in text


def test_remove_comment_no_op_when_no_comment(tmp_dir: Path) -> None:
    original = 'SECRET=abc\n'
    f = _write(tmp_dir / '.env', original)
    remove_comment(f, 'SECRET')
    assert f.read_text() == original


def test_remove_comment_missing_file_raises(tmp_dir: Path) -> None:
    with pytest.raises(CommentError, match='not found'):
        remove_comment(tmp_dir / 'nope.env', 'K')


def test_remove_comment_missing_key_raises(tmp_dir: Path) -> None:
    f = _write(tmp_dir / '.env', 'A=1\n')
    with pytest.raises(CommentError, match="'GHOST'"):
        remove_comment(f, 'GHOST')


def test_list_comments_returns_pairs(tmp_dir: Path) -> None:
    f = _write(tmp_dir / '.env', 'A=1  # first\nB=2\nC=3  # third\n')
    result = list_comments(f)
    assert result == [('A', 'first'), ('C', 'third')]


def test_list_comments_empty_when_none(tmp_dir: Path) -> None:
    f = _write(tmp_dir / '.env', 'A=1\nB=2\n')
    assert list_comments(f) == []


def test_list_comments_missing_file_raises(tmp_dir: Path) -> None:
    with pytest.raises(CommentError, match='not found'):
        list_comments(tmp_dir / 'absent.env')


def test_set_and_list_roundtrip(tmp_dir: Path) -> None:
    f = _write(tmp_dir / '.env', 'X=10\nY=20\n')
    set_comment(f, 'X', 'multiplier')
    set_comment(f, 'Y', 'offset')
    pairs = list_comments(f)
    assert ('X', 'multiplier') in pairs
    assert ('Y', 'offset') in pairs
