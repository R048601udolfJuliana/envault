"""Tests for envault.env_count."""
from __future__ import annotations

import pytest
from pathlib import Path

from envault.env_count import CountError, CountResult, count_keys


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, text: str) -> Path:
    p.write_text(text, encoding="utf-8")
    return p


def test_count_basic(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "FOO=bar\nBAZ=qux\n")
    result = count_keys(f)
    assert result.total == 2
    assert result.non_empty == 2
    assert result.empty == 0


def test_count_empty_values(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "FOO=\nBAR=hello\nBAZ=\n")
    result = count_keys(f)
    assert result.total == 3
    assert result.empty == 2
    assert result.non_empty == 1


def test_count_ignores_comments_and_blanks(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "# comment\n\nFOO=bar\n")
    result = count_keys(f)
    assert result.total == 1


def test_count_missing_file_raises(tmp_dir: Path) -> None:
    with pytest.raises(CountError, match="not found"):
        count_keys(tmp_dir / "missing.env")


def test_count_pattern_matched(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "DB_HOST=localhost\nDB_PORT=5432\nAPP_KEY=secret\n")
    result = count_keys(f, pattern="^DB_")
    assert result.matched == 2
    assert result.pattern == "^DB_"


def test_count_pattern_case_insensitive_default(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "db_host=localhost\nDB_PORT=5432\nAPP=x\n")
    result = count_keys(f, pattern="db_")
    assert result.matched == 2


def test_count_pattern_case_sensitive(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "db_host=localhost\nDB_PORT=5432\n")
    result = count_keys(f, pattern="db_", case_sensitive=True)
    assert result.matched == 1


def test_count_invalid_pattern_raises(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "FOO=bar\n")
    with pytest.raises(CountError, match="Invalid pattern"):
        count_keys(f, pattern="[invalid")


def test_summary_lines_without_pattern(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "A=1\nB=\n")
    result = count_keys(f)
    lines = result.summary_lines()
    assert any("Total" in l for l in lines)
    assert not any("Matched" in l for l in lines)


def test_summary_lines_with_pattern(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "DB_HOST=x\nAPP=y\n")
    result = count_keys(f, pattern="DB")
    lines = result.summary_lines()
    assert any("Matched" in l for l in lines)
