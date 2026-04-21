"""Tests for envault.env_numeric."""

from __future__ import annotations

from pathlib import Path

import pytest

from envault.env_numeric import NumericError, NumericResult, analyze_numeric


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content, encoding="utf-8")
    return p


def test_analyze_basic(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "PORT=8080\nRATIO=3.14\nNAME=alice\n")
    result = analyze_numeric(f)
    assert "PORT" in result.integers
    assert result.integers["PORT"] == 8080
    assert "RATIO" in result.floats
    assert abs(result.floats["RATIO"] - 3.14) < 1e-9
    assert "NAME" in result.non_numeric


def test_analyze_ignores_comments_and_blanks(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "# comment\n\nTIMEOUT=30\n")
    result = analyze_numeric(f)
    assert list(result.integers.keys()) == ["TIMEOUT"]
    assert result.floats == {}
    assert result.non_numeric == []


def test_analyze_quoted_integer(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", 'WORKERS="4"\n')
    result = analyze_numeric(f)
    assert "WORKERS" in result.integers
    assert result.integers["WORKERS"] == 4


def test_analyze_empty_file(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "")
    result = analyze_numeric(f)
    assert result.integers == {}
    assert result.floats == {}
    assert result.non_numeric == []


def test_analyze_missing_file_raises(tmp_dir: Path) -> None:
    with pytest.raises(NumericError, match="not found"):
        analyze_numeric(tmp_dir / "missing.env")


def test_summary_lines_counts(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "A=1\nB=2.5\nC=hello\n")
    result = analyze_numeric(f)
    lines = result.summary_lines()
    assert any("1" in l and "Integer" in l for l in lines)
    assert any("1" in l and "Float" in l for l in lines)
    assert any("1" in l and "Other" in l for l in lines)


def test_numeric_result_has_no_duplicates(tmp_dir: Path) -> None:
    """A key should appear in exactly one category."""
    f = _write(tmp_dir / ".env", "X=42\nY=hello\nZ=0.5\n")
    result = analyze_numeric(f)
    all_keys = (
        list(result.integers) + list(result.floats) + result.non_numeric
    )
    assert len(all_keys) == len(set(all_keys))
