"""Tests for envault.env_merge."""
from pathlib import Path
import pytest

from envault.env_merge import (
    MergeError,
    MergeConflict,
    merge_env,
    write_merged,
    _parse_env,
)


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content)
    return p


# --- _parse_env ---

def test_parse_env_basic():
    result = _parse_env("FOO=bar\nBAZ=qux\n")
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_parse_env_strips_quotes():
    assert _parse_env('KEY="hello"') == {"KEY": "hello"}


def test_parse_env_ignores_comments():
    result = _parse_env("# comment\nKEY=val\n")
    assert "KEY" in result and len(result) == 1


# --- merge_env ---

def test_merge_no_conflicts(tmp_dir):
    base = _write(tmp_dir / "base.env", "A=1\nB=2\n")
    other = _write(tmp_dir / "other.env", "C=3\n")
    result = merge_env(base, other)
    assert result.merged == {"A": "1", "B": "2", "C": "3"}
    assert not result.has_conflicts


def test_merge_conflict_strategy_ours(tmp_dir):
    base = _write(tmp_dir / "base.env", "A=base\n")
    other = _write(tmp_dir / "other.env", "A=other\n")
    result = merge_env(base, other, strategy="ours")
    assert result.merged["A"] == "base"
    assert result.has_conflicts
    assert result.conflicts[0] == MergeConflict("A", "base", "other")


def test_merge_conflict_strategy_theirs(tmp_dir):
    base = _write(tmp_dir / "base.env", "A=base\n")
    other = _write(tmp_dir / "other.env", "A=other\n")
    result = merge_env(base, other, strategy="theirs")
    assert result.merged["A"] == "other"
    assert result.has_conflicts


def test_merge_conflict_strategy_error(tmp_dir):
    base = _write(tmp_dir / "base.env", "A=base\n")
    other = _write(tmp_dir / "other.env", "A=other\n")
    with pytest.raises(MergeError, match="Conflict on key"):
        merge_env(base, other, strategy="error")


def test_merge_unknown_strategy_raises(tmp_dir):
    base = _write(tmp_dir / "base.env", "A=1\n")
    other = _write(tmp_dir / "other.env", "B=2\n")
    with pytest.raises(MergeError, match="Unknown strategy"):
        merge_env(base, other, strategy="bogus")


def test_merge_missing_base_raises(tmp_dir):
    other = _write(tmp_dir / "other.env", "A=1\n")
    with pytest.raises(MergeError, match="Base file not found"):
        merge_env(tmp_dir / "missing.env", other)


def test_merge_missing_other_raises(tmp_dir):
    base = _write(tmp_dir / "base.env", "A=1\n")
    with pytest.raises(MergeError, match="Other file not found"):
        merge_env(base, tmp_dir / "missing.env")


def test_summary_lines_no_conflicts(tmp_dir):
    base = _write(tmp_dir / "base.env", "A=1\n")
    other = _write(tmp_dir / "other.env", "B=2\n")
    result = merge_env(base, other)
    lines = result.summary_lines()
    assert lines[0].startswith("Merged keys:")
    assert len(lines) == 1


def test_write_merged(tmp_dir):
    base = _write(tmp_dir / "base.env", "A=1\n")
    other = _write(tmp_dir / "other.env", "B=2\n")
    result = merge_env(base, other)
    dest = tmp_dir / "merged.env"
    write_merged(result, dest)
    content = dest.read_text()
    assert "A=1" in content
    assert "B=2" in content
