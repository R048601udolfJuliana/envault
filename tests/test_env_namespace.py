"""Tests for envault.env_namespace."""
from __future__ import annotations

from pathlib import Path

import pytest

from envault.env_namespace import NamespaceError, apply_namespace, strip_namespace


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content)
    return p


# --- apply_namespace ---

def test_apply_namespace_basic(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "DB_HOST=localhost\nDB_PORT=5432\n")
    apply_namespace(f, "APP_")
    assert f.read_text() == "APP_DB_HOST=localhost\nAPP_DB_PORT=5432\n"


def test_apply_namespace_skips_already_prefixed(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "APP_DB_HOST=localhost\nDB_PORT=5432\n")
    apply_namespace(f, "APP_")
    text = f.read_text()
    assert text.count("APP_APP_") == 0
    assert "APP_DB_PORT=5432" in text


def test_apply_namespace_preserves_comments_and_blanks(tmp_dir: Path) -> None:
    content = "# comment\n\nKEY=val\n"
    f = _write(tmp_dir / ".env", content)
    apply_namespace(f, "NS_")
    result = f.read_text()
    assert "# comment" in result
    assert "NS_KEY=val" in result


def test_apply_namespace_writes_to_dest(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "KEY=value\n")
    dest = tmp_dir / ".env.namespaced"
    out = apply_namespace(src, "X_", dest)
    assert out == dest.resolve()
    assert dest.read_text() == "X_KEY=value\n"
    assert src.read_text() == "KEY=value\n"  # source unchanged


def test_apply_namespace_empty_namespace_raises(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "KEY=val\n")
    with pytest.raises(NamespaceError):
        apply_namespace(f, "")


def test_apply_namespace_missing_file_raises(tmp_dir: Path) -> None:
    with pytest.raises(NamespaceError):
        apply_namespace(tmp_dir / "missing.env", "NS_")


# --- strip_namespace ---

def test_strip_namespace_basic(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "APP_DB_HOST=localhost\nAPP_DB_PORT=5432\n")
    _, count = strip_namespace(f, "APP_")
    assert count == 2
    assert f.read_text() == "DB_HOST=localhost\nDB_PORT=5432\n"


def test_strip_namespace_leaves_non_matching_unchanged(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "APP_KEY=val\nOTHER=x\n")
    _, count = strip_namespace(f, "APP_")
    assert count == 1
    text = f.read_text()
    assert "OTHER=x" in text
    assert "KEY=val" in text


def test_strip_namespace_returns_zero_when_no_match(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "KEY=val\n")
    _, count = strip_namespace(f, "APP_")
    assert count == 0


def test_strip_namespace_empty_namespace_raises(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "KEY=val\n")
    with pytest.raises(NamespaceError):
        strip_namespace(f, "")


def test_strip_namespace_missing_file_raises(tmp_dir: Path) -> None:
    with pytest.raises(NamespaceError):
        strip_namespace(tmp_dir / "missing.env", "NS_")
