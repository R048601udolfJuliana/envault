"""Tests for envault.env_quote."""
from __future__ import annotations

from pathlib import Path

import pytest

from envault.env_quote import QuoteError, _strip_quotes, _apply_quote, quote_env


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content, encoding="utf-8")
    return p


# --- unit helpers ---

def test_strip_quotes_double():
    assert _strip_quotes('"hello"') == "hello"


def test_strip_quotes_single():
    assert _strip_quotes("'world'") == "world"


def test_strip_quotes_bare():
    assert _strip_quotes("bare") == "bare"


def test_apply_quote_double():
    assert _apply_quote("hello", "double") == '"hello"'


def test_apply_quote_single():
    assert _apply_quote('"hello"', "single") == "'hello'"


def test_apply_quote_none_strips():
    assert _apply_quote('"hello"', "none") == "hello"


# --- quote_env integration ---

def test_quote_env_adds_double_quotes(tmp_dir: Path):
    src = _write(tmp_dir / ".env", "KEY=value\nOTHER=foo\n")
    result = quote_env(src, style="double")
    text = src.read_text()
    assert 'KEY="value"' in text
    assert 'OTHER="foo"' in text
    assert result == src.resolve()


def test_quote_env_single_style(tmp_dir: Path):
    src = _write(tmp_dir / ".env", "KEY=value\n")
    quote_env(src, style="single")
    assert "KEY='value'" in src.read_text()


def test_quote_env_none_strips_existing(tmp_dir: Path):
    src = _write(tmp_dir / ".env", 'KEY="value"\n')
    quote_env(src, style="none")
    assert "KEY=value" in src.read_text()


def test_quote_env_restricts_to_keys(tmp_dir: Path):
    src = _write(tmp_dir / ".env", "A=one\nB=two\n")
    quote_env(src, style="double", keys=["A"])
    text = src.read_text()
    assert 'A="one"' in text
    assert "B=two" in text


def test_quote_env_preserves_comments(tmp_dir: Path):
    src = _write(tmp_dir / ".env", "# comment\nKEY=val\n")
    quote_env(src, style="double")
    text = src.read_text()
    assert text.startswith("# comment\n")


def test_quote_env_writes_to_dest(tmp_dir: Path):
    src = _write(tmp_dir / ".env", "KEY=value\n")
    dest = tmp_dir / "out.env"
    quote_env(src, dest=dest, style="single")
    assert dest.exists()
    assert "KEY='value'" in dest.read_text()
    # source unchanged
    assert src.read_text() == "KEY=value\n"


def test_quote_env_missing_file_raises(tmp_dir: Path):
    with pytest.raises(QuoteError, match="not found"):
        quote_env(tmp_dir / "missing.env", style="double")


def test_quote_env_invalid_style_raises(tmp_dir: Path):
    src = _write(tmp_dir / ".env", "KEY=val\n")
    with pytest.raises(QuoteError, match="Unknown quote style"):
        quote_env(src, style="curly")  # type: ignore[arg-type]
