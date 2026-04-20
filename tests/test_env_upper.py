"""Tests for envault.env_upper."""

from __future__ import annotations

from pathlib import Path

import pytest

from envault.env_upper import UpperError, _parse_lines, upper_env


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# _parse_lines
# ---------------------------------------------------------------------------

def test_parse_lines_already_upper(tmp_dir: Path) -> None:
    pairs = _parse_lines("KEY=value\n")
    assert pairs == [("KEY=value\n", "KEY=value\n")]


def test_parse_lines_lowercase_key(tmp_dir: Path) -> None:
    pairs = _parse_lines("key=value\n")
    assert pairs == [("key=value\n", "KEY=value\n")]


def test_parse_lines_mixed_case_key(tmp_dir: Path) -> None:
    pairs = _parse_lines("MyKey=hello\n")
    assert pairs == [("MyKey=hello\n", "MYKEY=hello\n")]


def test_parse_lines_preserves_comments(tmp_dir: Path) -> None:
    pairs = _parse_lines("# comment\n")
    assert pairs == [("# comment\n", "# comment\n")]


def test_parse_lines_preserves_blank_lines(tmp_dir: Path) -> None:
    pairs = _parse_lines("\n")
    assert pairs == [("\n", "\n")]


def test_parse_lines_no_equals_unchanged(tmp_dir: Path) -> None:
    pairs = _parse_lines("NOEQUALS\n")
    assert pairs == [("NOEQUALS\n", "NOEQUALS\n")]


def test_parse_lines_value_with_equals(tmp_dir: Path) -> None:
    """Value containing '=' must not be mangled."""
    pairs = _parse_lines("url=http://x.com?a=1\n")
    assert pairs == [("url=http://x.com?a=1\n", "URL=http://x.com?a=1\n")]


# ---------------------------------------------------------------------------
# upper_env
# ---------------------------------------------------------------------------

def test_upper_env_in_place(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "db_host=localhost\ndb_port=5432\n")
    changed = upper_env(f)
    assert len(changed) == 2
    content = f.read_text()
    assert "DB_HOST=localhost" in content
    assert "DB_PORT=5432" in content


def test_upper_env_to_dest(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "api_key=secret\n")
    dest = tmp_dir / ".env.upper"
    upper_env(src, dest)
    assert dest.exists()
    assert "API_KEY=secret" in dest.read_text()
    # Source should be unchanged
    assert "api_key=secret" in src.read_text()


def test_upper_env_dry_run_does_not_write(tmp_dir: Path) -> None:
    original = "lower=val\n"
    f = _write(tmp_dir / ".env", original)
    changed = upper_env(f, dry_run=True)
    assert len(changed) == 1
    assert f.read_text() == original  # untouched


def test_upper_env_no_changes_returns_empty(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "ALREADY_UPPER=yes\n")
    changed = upper_env(f)
    assert changed == []


def test_upper_env_missing_file_raises(tmp_dir: Path) -> None:
    with pytest.raises(UpperError, match="not found"):
        upper_env(tmp_dir / "nonexistent.env")


def test_upper_env_preserves_comments_and_blanks(tmp_dir: Path) -> None:
    content = "# header\n\nlower=1\n# inline\nUPPER=2\n"
    f = _write(tmp_dir / ".env", content)
    upper_env(f)
    result = f.read_text()
    assert result.startswith("# header\n\nLOWER=1\n# inline\nUPPER=2\n")
