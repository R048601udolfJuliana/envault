"""Tests for envault.env_prefix."""
from __future__ import annotations

from pathlib import Path

import pytest

from envault.env_prefix import PrefixError, add_prefix, strip_prefix


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, text: str) -> Path:
    p.write_text(text, encoding="utf-8")
    return p


# --- add_prefix ---

def test_add_prefix_basic(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "DB_HOST=localhost\nDB_PORT=5432\n")
    add_prefix(f, "APP_")
    result = f.read_text()
    assert "APP_DB_HOST=localhost" in result
    assert "APP_DB_PORT=5432" in result


def test_add_prefix_skips_already_prefixed(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "APP_KEY=val\n")
    add_prefix(f, "APP_")
    content = f.read_text()
    assert content.count("APP_KEY") == 1


def test_add_prefix_preserves_comments_and_blanks(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "# comment\n\nFOO=bar\n")
    add_prefix(f, "X_")
    content = f.read_text()
    assert "# comment" in content
    assert "X_FOO=bar" in content


def test_add_prefix_writes_to_dest(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "KEY=val\n")
    dest = tmp_dir / ".env.out"
    add_prefix(src, "P_", dest)
    assert dest.exists()
    assert "P_KEY=val" in dest.read_text()
    assert "KEY=val" in src.read_text()  # original untouched


def test_add_prefix_empty_prefix_raises(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "KEY=val\n")
    with pytest.raises(PrefixError, match="empty"):
        add_prefix(f, "")


def test_add_prefix_missing_file_raises(tmp_dir: Path) -> None:
    with pytest.raises(PrefixError, match="not found"):
        add_prefix(tmp_dir / "missing.env", "X_")


# --- strip_prefix ---

def test_strip_prefix_basic(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "APP_HOST=localhost\nAPP_PORT=5432\n")
    strip_prefix(f, "APP_")
    content = f.read_text()
    assert "HOST=localhost" in content
    assert "PORT=5432" in content


def test_strip_prefix_leaves_unmatched_keys(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "APP_KEY=val\nOTHER=x\n")
    strip_prefix(f, "APP_")
    content = f.read_text()
    assert "KEY=val" in content
    assert "OTHER=x" in content


def test_strip_prefix_empty_prefix_raises(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "KEY=val\n")
    with pytest.raises(PrefixError, match="empty"):
        strip_prefix(f, "")


def test_strip_prefix_missing_file_raises(tmp_dir: Path) -> None:
    with pytest.raises(PrefixError, match="not found"):
        strip_prefix(tmp_dir / "missing.env", "X_")


def test_strip_prefix_returns_dest_path(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "PRE_KEY=val\n")
    dest = tmp_dir / "out.env"
    result = strip_prefix(src, "PRE_", dest)
    assert result == dest
    assert "KEY=val" in dest.read_text()
