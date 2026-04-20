"""Tests for envault.env_trim."""
from __future__ import annotations

from pathlib import Path

import pytest

from envault.env_trim import TrimError, _parse_lines, trim_env


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content, encoding="utf-8")
    return p


def test_parse_lines_no_change_needed():
    lines = _parse_lines("KEY=value\n")
    assert lines == [("KEY=value\n", "KEY=value\n", False)]


def test_parse_lines_detects_trailing_space():
    lines = _parse_lines("KEY=value   \n")
    assert lines[0][2] is True
    assert lines[0][1] == "KEY=value\n"


def test_parse_lines_detects_leading_space_in_value():
    lines = _parse_lines("KEY=  value\n")
    assert lines[0][2] is True
    assert lines[0][1] == "KEY=value\n"


def test_parse_lines_ignores_comments():
    lines = _parse_lines("# comment\n")
    assert lines[0][2] is False


def test_parse_lines_ignores_blank_lines():
    lines = _parse_lines("\n")
    assert lines[0][2] is False


def test_trim_env_writes_in_place(tmp_dir: Path):
    f = _write(tmp_dir / ".env", "A=  hello  \nB=world\n")
    count = trim_env(f)
    assert count == 1
    assert f.read_text(encoding="utf-8") == "A=hello\nB=world\n"


def test_trim_env_writes_to_dest(tmp_dir: Path):
    src = _write(tmp_dir / ".env", "A=  hi  \n")
    dest = tmp_dir / ".env.trimmed"
    trim_env(src, dest)
    assert dest.read_text(encoding="utf-8") == "A=hi\n"
    # source unchanged
    assert src.read_text(encoding="utf-8") == "A=  hi  \n"


def test_trim_env_dry_run_does_not_write(tmp_dir: Path):
    original = "A=  hello  \n"
    f = _write(tmp_dir / ".env", original)
    count = trim_env(f, dry_run=True)
    assert count == 1
    assert f.read_text(encoding="utf-8") == original


def test_trim_env_returns_zero_when_clean(tmp_dir: Path):
    f = _write(tmp_dir / ".env", "A=clean\nB=also_clean\n")
    assert trim_env(f) == 0


def test_trim_env_missing_file_raises(tmp_dir: Path):
    with pytest.raises(TrimError, match="not found"):
        trim_env(tmp_dir / "missing.env")
