"""Tests for envault.env_placeholder."""
from pathlib import Path

import pytest

from envault.env_placeholder import (
    PlaceholderError,
    PlaceholderResult,
    scan_placeholders,
)


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, text: str) -> Path:
    p.write_text(text, encoding="utf-8")
    return p


def test_scan_returns_placeholder_result_type(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "KEY=value\n")
    result = scan_placeholders(f)
    assert isinstance(result, PlaceholderResult)


def test_no_placeholders_found(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "DB_HOST=localhost\nDB_PORT=5432\n")
    result = scan_placeholders(f)
    assert not result.found
    assert result.matches == []


def test_detects_angle_bracket_placeholder(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "API_KEY=<YOUR_API_KEY>\n")
    result = scan_placeholders(f)
    assert result.found
    assert result.matches[0].key == "API_KEY"
    assert result.matches[0].value == "<YOUR_API_KEY>"


def test_detects_dollar_brace_placeholder(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "TOKEN=${FILL_ME_IN}\n")
    result = scan_placeholders(f)
    assert result.found
    assert result.matches[0].key == "TOKEN"


def test_detects_double_brace_placeholder(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "SECRET={{secret_value}}\n")
    result = scan_placeholders(f)
    assert result.found


def test_detects_changeme_case_insensitive(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "PASSWORD=CHANGEME\n")
    result = scan_placeholders(f)
    assert result.found
    assert result.matches[0].key == "PASSWORD"


def test_detects_todo_value(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "CERT_PATH=todo\n")
    result = scan_placeholders(f)
    assert result.found


def test_ignores_comments_and_blanks(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "# <comment>\n\nKEY=real_value\n")
    result = scan_placeholders(f)
    assert not result.found


def test_strips_quotes_before_matching(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", 'KEY="<REPLACE_ME>"\n')
    result = scan_placeholders(f)
    assert result.found
    assert result.matches[0].value == "<REPLACE_ME>"


def test_line_number_recorded(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "GOOD=ok\nBAD=<fill>\n")
    result = scan_placeholders(f)
    assert result.matches[0].line_no == 2


def test_summary_lines_no_matches(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "K=v\n")
    result = scan_placeholders(f)
    assert result.summary_lines() == ["No placeholder values detected."]


def test_summary_lines_with_matches(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "K=<val>\n")
    result = scan_placeholders(f)
    lines = result.summary_lines()
    assert lines[0].startswith("Found 1 placeholder")
    assert any("K" in l for l in lines)


def test_missing_file_raises(tmp_dir: Path) -> None:
    with pytest.raises(PlaceholderError, match="not found"):
        scan_placeholders(tmp_dir / "nonexistent.env")
