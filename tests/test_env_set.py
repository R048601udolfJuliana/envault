"""Tests for envault.env_set."""
from __future__ import annotations

import pytest
from pathlib import Path

from envault.env_set import SetError, set_key, unset_key


@pytest.fixture
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, text: str) -> Path:
    p.write_text(text, encoding="utf-8")
    return p


def test_set_key_adds_to_new_file(tmp_dir: Path) -> None:
    f = tmp_dir / ".env"
    added = set_key(f, "FOO", "bar")
    assert added is True
    assert "FOO=bar" in f.read_text()


def test_set_key_updates_existing(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "FOO=old\nBAR=baz\n")
    added = set_key(f, "FOO", "new")
    assert added is False
    text = f.read_text()
    assert "FOO=new" in text
    assert "FOO=old" not in text
    assert "BAR=baz" in text


def test_set_key_appends_when_missing(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "FOO=bar\n")
    set_key(f, "NEW", "val")
    text = f.read_text()
    assert "NEW=val" in text
    assert "FOO=bar" in text


def test_set_key_no_create_raises(tmp_dir: Path) -> None:
    f = tmp_dir / ".env"
    with pytest.raises(SetError, match="not found"):
        set_key(f, "X", "y", create=False)


def test_set_key_invalid_name_raises(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "")
    with pytest.raises(SetError, match="Invalid key"):
        set_key(f, "123BAD", "val")


def test_unset_key_removes_key(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "FOO=bar\nBAR=baz\n")
    removed = unset_key(f, "FOO")
    assert removed is True
    text = f.read_text()
    assert "FOO" not in text
    assert "BAR=baz" in text


def test_unset_key_returns_false_when_missing(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "FOO=bar\n")
    removed = unset_key(f, "GHOST")
    assert removed is False


def test_unset_key_missing_file_raises(tmp_dir: Path) -> None:
    f = tmp_dir / ".env"
    with pytest.raises(SetError, match="not found"):
        unset_key(f, "FOO")


def test_set_key_preserves_comments(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "# comment\nFOO=old\n")
    set_key(f, "FOO", "new")
    text = f.read_text()
    assert "# comment" in text
    assert "FOO=new" in text
