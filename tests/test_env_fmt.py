"""Tests for envault.env_fmt."""
from pathlib import Path
import pytest
from envault.env_fmt import FmtError, format_env, _fmt_line


@pytest.fixture
def tmp_dir(tmp_path):
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content)
    return p


def test_fmt_line_plain():
    assert _fmt_line("KEY = value\n") == "KEY=value\n"


def test_fmt_line_strips_existing_double_quotes():
    assert _fmt_line('KEY="value"\n') == "KEY=value\n"


def test_fmt_line_strips_existing_single_quotes():
    assert _fmt_line("KEY='value'\n") == "KEY=value\n"


def test_fmt_line_quote_values():
    assert _fmt_line("KEY=hello\n", quote_values=True) == 'KEY="hello"\n'


def test_fmt_line_comment_unchanged():
    assert _fmt_line("# comment\n") == "# comment\n"


def test_fmt_line_blank_unchanged():
    assert _fmt_line("\n") == "\n"


def test_format_env_in_place(tmp_dir):
    f = _write(tmp_dir / ".env", "KEY = hello\nOTHER='world'\n")
    out = format_env(f)
    assert out == f
    lines = f.read_text().splitlines()
    assert "KEY=hello" in lines
    assert "OTHER=world" in lines


def test_format_env_to_dest(tmp_dir):
    src = _write(tmp_dir / ".env", "A = 1\n")
    dest = tmp_dir / ".env.fmt"
    out = format_env(src, dest=dest)
    assert out == dest
    assert dest.read_text().strip() == "A=1"
    assert src.read_text() == "A = 1\n"  # original untouched


def test_format_env_quote_values(tmp_dir):
    f = _write(tmp_dir / ".env", "KEY=value\n")
    format_env(f, quote_values=True)
    assert f.read_text().strip() == 'KEY="value"'


def test_format_env_missing_file_raises(tmp_dir):
    with pytest.raises(FmtError, match="not found"):
        format_env(tmp_dir / "missing.env")


def test_format_env_single_trailing_newline(tmp_dir):
    f = _write(tmp_dir / ".env", "A=1\nB=2\n\n\n")
    format_env(f)
    assert f.read_text().endswith("\n")
    assert not f.read_text().endswith("\n\n")
