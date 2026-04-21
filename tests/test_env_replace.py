"""Tests for envault.env_replace."""
from __future__ import annotations

import pytest
from pathlib import Path

from envault.env_replace import ReplaceError, replace_value


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content, encoding="utf-8")
    return p


def test_replace_basic(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "DB_HOST=localhost\nDB_PORT=5432\n")
    _, n = replace_value(f, "localhost", "db.prod.internal")
    assert n == 1
    assert "DB_HOST=db.prod.internal" in f.read_text()


def test_replace_regex(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "URL=http://example.com\n")
    _, n = replace_value(f, r"http://", "https://")
    assert n == 1
    assert "URL=https://example.com" in f.read_text()


def test_replace_literal_flag(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "PATH_VAR=/usr/local/bin\n")
    _, n = replace_value(f, "/usr/local/bin", "/opt/bin", literal=True)
    assert n == 1
    assert "PATH_VAR=/opt/bin" in f.read_text()


def test_replace_keys_filter(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "A=foo\nB=foo\n")
    _, n = replace_value(f, "foo", "bar", keys=["A"])
    assert n == 1
    text = f.read_text()
    assert "A=bar" in text
    assert "B=foo" in text


def test_replace_no_match_returns_zero(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "KEY=value\n")
    _, n = replace_value(f, "NOTFOUND", "x")
    assert n == 0


def test_replace_writes_to_dest(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "FOO=hello\n")
    dest = tmp_dir / ".env.out"
    resolved, n = replace_value(src, "hello", "world", dest=dest)
    assert resolved == dest
    assert dest.read_text() == "FOO=world\n"
    assert src.read_text() == "FOO=hello\n"  # original untouched


def test_replace_preserves_comments_and_blanks(tmp_dir: Path) -> None:
    content = "# comment\n\nFOO=bar\n"
    f = _write(tmp_dir / ".env", content)
    _, n = replace_value(f, "bar", "baz")
    assert n == 1
    assert f.read_text().startswith("# comment\n\n")


def test_replace_missing_file_raises(tmp_dir: Path) -> None:
    with pytest.raises(ReplaceError, match="not found"):
        replace_value(tmp_dir / "missing.env", "x", "y")


def test_replace_strips_quotes_before_matching(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", 'SECRET="old_secret"\n')
    _, n = replace_value(f, "old_secret", "new_secret")
    assert n == 1
    assert "SECRET=new_secret" in f.read_text()


def test_replace_count_limits_substitutions(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "VAL=aaa\n")
    _, n = replace_value(f, "a", "b", count=2)
    assert n == 1
    assert "VAL=bba" in f.read_text()
