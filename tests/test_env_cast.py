"""Tests for envault.env_cast."""
from __future__ import annotations

import pytest
from pathlib import Path

from envault.env_cast import CastError, _cast_value, _parse_env, cast_env


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content, encoding="utf-8")
    return p


# --- _parse_env ---

def test_parse_env_basic():
    pairs = _parse_env("FOO=bar\nBAZ=42\n")
    assert pairs == [("FOO", "bar"), ("BAZ", "42")]


def test_parse_env_strips_quotes():
    pairs = _parse_env('KEY="hello world"\n')
    assert pairs == [("KEY", "hello world")]


def test_parse_env_ignores_comments_and_blanks():
    pairs = _parse_env("# comment\n\nFOO=bar\n")
    assert pairs == [("FOO", "bar")]


def test_parse_env_skips_no_equals():
    pairs = _parse_env("NOEQUALS\nFOO=bar\n")
    assert pairs == [("FOO", "bar")]


# --- _cast_value ---

def test_cast_int():
    assert _cast_value("42", "int") == 42


def test_cast_float():
    assert _cast_value("3.14", "float") == pytest.approx(3.14)


def test_cast_bool_true_variants():
    for val in ("true", "yes", "1", "on", "True", "YES"):
        assert _cast_value(val, "bool") is True


def test_cast_bool_false_variants():
    for val in ("false", "no", "0", "off"):
        assert _cast_value(val, "bool") is False


def test_cast_list():
    assert _cast_value("a,b,c", "list") == ["a", "b", "c"]


def test_cast_list_strips_spaces():
    assert _cast_value("a, b , c", "list") == ["a", "b", "c"]


def test_cast_str_passthrough():
    assert _cast_value("hello", "str") == "hello"


def test_cast_unknown_hint_raises():
    with pytest.raises(CastError, match="Unknown type hint"):
        _cast_value("x", "bytes")


def test_cast_int_invalid_raises():
    with pytest.raises(CastError, match="Cannot cast"):
        _cast_value("notanint", "int")


def test_cast_bool_invalid_raises():
    with pytest.raises(CastError, match="Cannot cast"):
        _cast_value("maybe", "bool")


# --- cast_env ---

def test_cast_env_basic(tmp_dir: Path):
    f = _write(tmp_dir / ".env", "PORT=8080\nDEBUG=true\nNAME=myapp\n")
    result = cast_env(f, {"PORT": "int", "DEBUG": "bool"})
    assert result["PORT"] == 8080
    assert result["DEBUG"] is True
    assert result["NAME"] == "myapp"


def test_cast_env_missing_file_raises(tmp_dir: Path):
    with pytest.raises(CastError, match="File not found"):
        cast_env(tmp_dir / "nonexistent.env", {})


def test_cast_env_no_hints_returns_strings(tmp_dir: Path):
    f = _write(tmp_dir / ".env", "A=1\nB=hello\n")
    result = cast_env(f, {})
    assert result == {"A": "1", "B": "hello"}


def test_cast_env_list_hint(tmp_dir: Path):
    f = _write(tmp_dir / ".env", "HOSTS=a.com,b.com,c.com\n")
    result = cast_env(f, {"HOSTS": "list"})
    assert result["HOSTS"] == ["a.com", "b.com", "c.com"]
