"""Tests for envault.env_unique."""
from pathlib import Path

import pytest

from envault.env_unique import UniqueError, UniqueResult, deduplicate_env


@pytest.fixture
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, text: str) -> Path:
    p.write_text(text, encoding="utf-8")
    return p


def test_no_duplicates_returns_empty_result(tmp_dir):
    f = _write(tmp_dir / ".env", "FOO=1\nBAR=2\n")
    result = deduplicate_env(f)
    assert not result.has_duplicates
    assert result.duplicates == []


def test_detects_duplicate_key(tmp_dir):
    f = _write(tmp_dir / ".env", "FOO=1\nBAR=2\nFOO=3\n")
    result = deduplicate_env(f)
    assert result.has_duplicates
    assert any(k == "FOO" for k, _ in result.duplicates)


def test_keep_last_removes_first_occurrence(tmp_dir):
    f = _write(tmp_dir / ".env", "FOO=first\nBAR=2\nFOO=last\n")
    result = deduplicate_env(f, keep="last")
    content = f.read_text()
    assert "FOO=last" in content
    assert "FOO=first" not in content


def test_keep_first_removes_last_occurrence(tmp_dir):
    f = _write(tmp_dir / ".env", "FOO=first\nBAR=2\nFOO=last\n")
    result = deduplicate_env(f, keep="first")
    content = f.read_text()
    assert "FOO=first" in content
    assert "FOO=last" not in content


def test_write_to_separate_dest(tmp_dir):
    src = _write(tmp_dir / ".env", "FOO=1\nFOO=2\n")
    dest = tmp_dir / ".env.out"
    deduplicate_env(src, dest)
    assert dest.exists()
    assert src.read_text() == "FOO=1\nFOO=2\n"  # src unchanged


def test_missing_file_raises(tmp_dir):
    with pytest.raises(UniqueError, match="File not found"):
        deduplicate_env(tmp_dir / "missing.env")


def test_invalid_keep_strategy_raises(tmp_dir):
    f = _write(tmp_dir / ".env", "FOO=1\n")
    with pytest.raises(UniqueError, match="Invalid keep strategy"):
        deduplicate_env(f, keep="middle")


def test_comments_and_blanks_preserved(tmp_dir):
    content = "# comment\nFOO=1\n\nBAR=2\nFOO=3\n"
    f = _write(tmp_dir / ".env", content)
    result = deduplicate_env(f)
    out = f.read_text()
    assert "# comment" in out
    assert "\n\n" in out or "\n" in out  # blank line kept


def test_summary_lines_no_duplicates(tmp_dir):
    f = _write(tmp_dir / ".env", "A=1\n")
    result = deduplicate_env(f)
    assert result.summary_lines() == ["No duplicate keys found."]


def test_summary_lines_with_duplicates(tmp_dir):
    f = _write(tmp_dir / ".env", "A=1\nA=2\n")
    result = deduplicate_env(f)
    lines = result.summary_lines()
    assert lines[0].startswith("Found")
    assert any("A" in l for l in lines)
