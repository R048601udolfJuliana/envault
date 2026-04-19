"""Tests for envault.env_stats"""
import pytest
from pathlib import Path
from envault.env_stats import StatsError, compute_stats, EnvStats


@pytest.fixture
def tmp_dir(tmp_path):
    return tmp_path


def _write(p: Path, text: str) -> Path:
    p.write_text(text, encoding="utf-8")
    return p


def test_compute_stats_basic(tmp_dir):
    f = _write(tmp_dir / ".env", "KEY1=value1\nKEY2=value2\n")
    s = compute_stats(f)
    assert s.total_keys == 2
    assert s.empty_values == 0
    assert s.duplicate_keys == []


def test_compute_stats_empty_value(tmp_dir):
    f = _write(tmp_dir / ".env", "KEY1=\nKEY2=hello\n")
    s = compute_stats(f)
    assert s.total_keys == 2
    assert s.empty_values == 1


def test_compute_stats_comments_and_blanks(tmp_dir):
    f = _write(tmp_dir / ".env", "# comment\n\nKEY=val\n")
    s = compute_stats(f)
    assert s.comment_lines == 1
    assert s.blank_lines == 1
    assert s.total_keys == 1


def test_compute_stats_longest_key(tmp_dir):
    f = _write(tmp_dir / ".env", "A=1\nLONGER_KEY=2\n")
    s = compute_stats(f)
    assert s.longest_key == "LONGER_KEY"


def test_compute_stats_longest_value_key(tmp_dir):
    f = _write(tmp_dir / ".env", "A=short\nB=much_longer_value\n")
    s = compute_stats(f)
    assert s.longest_value_key == "B"


def test_compute_stats_duplicate_keys(tmp_dir):
    f = _write(tmp_dir / ".env", "KEY=a\nKEY=b\nOTHER=c\n")
    s = compute_stats(f)
    assert "KEY" in s.duplicate_keys
    assert "OTHER" not in s.duplicate_keys


def test_compute_stats_missing_file_raises(tmp_dir):
    with pytest.raises(StatsError, match="not found"):
        compute_stats(tmp_dir / "nonexistent.env")


def test_summary_lines_no_duplicates(tmp_dir):
    f = _write(tmp_dir / ".env", "X=1\n")
    s = compute_stats(f)
    lines = s.summary_lines()
    assert any("Total keys" in l for l in lines)
    assert not any("Duplicate" in l for l in lines)


def test_summary_lines_with_duplicates(tmp_dir):
    f = _write(tmp_dir / ".env", "X=1\nX=2\n")
    s = compute_stats(f)
    lines = s.summary_lines()
    assert any("Duplicate" in l for l in lines)
