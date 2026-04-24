"""Tests for envault.env_tokenize."""
from pathlib import Path

import pytest

from envault.env_tokenize import (
    TokenizeError,
    TokenizeResult,
    TokenizedEntry,
    _detect_type,
    tokenize_env,
)


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content, encoding="utf-8")
    return p


# --- _detect_type ---

def test_detect_url():
    assert _detect_type("https://example.com") == "url"


def test_detect_email():
    assert _detect_type("user@example.com") == "email"


def test_detect_uuid():
    assert _detect_type("123e4567-e89b-12d3-a456-426614174000") == "uuid"


def test_detect_boolean():
    for v in ("true", "false", "yes", "no", "1", "0", "True", "YES"):
        assert _detect_type(v) == "boolean", v


def test_detect_integer():
    assert _detect_type("42") == "integer"
    assert _detect_type("-7") == "integer"


def test_detect_float():
    assert _detect_type("3.14") == "float"


def test_detect_path():
    assert _detect_type("/var/log/app") == "path"
    assert _detect_type("./relative/path") == "path"


def test_detect_string():
    assert _detect_type("some-random-string") == "string"


def test_detect_strips_quotes():
    assert _detect_type('"42"') == "integer"
    assert _detect_type("'true'") == "boolean"


# --- tokenize_env ---

def test_tokenize_basic(tmp_dir):
    f = _write(tmp_dir / ".env", "PORT=8080\nDEBUG=true\nNAME=myapp\n")
    result = tokenize_env(f)
    assert isinstance(result, TokenizeResult)
    assert len(result.entries) == 3
    types = {e.key: e.token_type for e in result.entries}
    assert types["PORT"] == "integer"
    assert types["DEBUG"] == "boolean"
    assert types["NAME"] == "string"


def test_tokenize_ignores_comments_and_blanks(tmp_dir):
    f = _write(tmp_dir / ".env", "# comment\n\nKEY=value\n")
    result = tokenize_env(f)
    assert len(result.entries) == 1


def test_tokenize_missing_file_raises(tmp_dir):
    with pytest.raises(TokenizeError, match="not found"):
        tokenize_env(tmp_dir / "nonexistent.env")


def test_tokenize_by_type(tmp_dir):
    f = _write(tmp_dir / ".env", "PORT=3000\nHOST=https://api.example.com\nNAME=app\n")
    result = tokenize_env(f)
    urls = result.by_type("url")
    assert len(urls) == 1
    assert urls[0].key == "HOST"


def test_tokenize_summary_lines(tmp_dir):
    f = _write(tmp_dir / ".env", "PORT=80\nDEBUG=false\nNAME=app\n")
    result = tokenize_env(f)
    lines = result.summary_lines()
    assert any("Total keys: 3" in l for l in lines)
    assert any("integer" in l for l in lines)
    assert any("boolean" in l for l in lines)
    assert any("string" in l for l in lines)


def test_tokenized_entry_str():
    e = TokenizedEntry(key="PORT", raw_value="8080", token_type="integer")
    s = str(e)
    assert "PORT" in s
    assert "integer" in s
