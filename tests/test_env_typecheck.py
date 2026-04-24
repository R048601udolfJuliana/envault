"""Tests for envault.env_typecheck."""
from __future__ import annotations

from pathlib import Path

import pytest

from envault.env_typecheck import (
    TypeCheckError,
    TypeCheckResult,
    TypeIssue,
    typecheck_env,
)


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content)
    return p


# ---------------------------------------------------------------------------
# typecheck_env
# ---------------------------------------------------------------------------

def test_typecheck_all_valid(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "PORT=8080\nDEBUG=true\nRATE=3.14\n")
    result = typecheck_env(f, {"PORT": "int", "DEBUG": "bool", "RATE": "float"})
    assert result.ok


def test_typecheck_invalid_int(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "PORT=not_a_number\n")
    result = typecheck_env(f, {"PORT": "int"})
    assert not result.ok
    assert result.issues[0].key == "PORT"
    assert result.issues[0].expected_type == "int"


def test_typecheck_invalid_float(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "RATE=abc\n")
    result = typecheck_env(f, {"RATE": "float"})
    assert not result.ok


def test_typecheck_valid_bool_variants(tmp_dir: Path) -> None:
    for val in ("true", "false", "1", "0", "yes", "no", "on", "off"):
        f = _write(tmp_dir / ".env", f"FLAG={val}\n")
        result = typecheck_env(f, {"FLAG": "bool"})
        assert result.ok, f"Expected ok for FLAG={val}"


def test_typecheck_invalid_bool(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "FLAG=maybe\n")
    result = typecheck_env(f, {"FLAG": "bool"})
    assert not result.ok


def test_typecheck_valid_url(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "API=https://example.com\n")
    result = typecheck_env(f, {"API": "url"})
    assert result.ok


def test_typecheck_invalid_url(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "API=ftp://example.com\n")
    result = typecheck_env(f, {"API": "url"})
    assert not result.ok


def test_typecheck_valid_email(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "EMAIL=user@example.com\n")
    result = typecheck_env(f, {"EMAIL": "email"})
    assert result.ok


def test_typecheck_invalid_email(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "EMAIL=not-an-email\n")
    result = typecheck_env(f, {"EMAIL": "email"})
    assert not result.ok


def test_typecheck_missing_key_is_skipped(tmp_dir: Path) -> None:
    """Keys absent from the env file are not reported as type errors."""
    f = _write(tmp_dir / ".env", "OTHER=hello\n")
    result = typecheck_env(f, {"PORT": "int"})
    assert result.ok


def test_typecheck_quoted_value_stripped(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", 'PORT="8080"\n')
    result = typecheck_env(f, {"PORT": "int"})
    assert result.ok


def test_typecheck_missing_file_raises(tmp_dir: Path) -> None:
    with pytest.raises(TypeCheckError, match="not found"):
        typecheck_env(tmp_dir / "missing.env", {"PORT": "int"})


def test_typecheck_unknown_type_raises(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "PORT=8080\n")
    with pytest.raises(TypeCheckError, match="unknown type"):
        typecheck_env(f, {"PORT": "integer"})


def test_typecheck_summary_lines_ok(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "PORT=9000\n")
    result = typecheck_env(f, {"PORT": "int"})
    lines = result.summary_lines()
    assert len(lines) == 1
    assert "match" in lines[0]


def test_typecheck_summary_lines_issues(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "PORT=bad\n")
    result = typecheck_env(f, {"PORT": "int"})
    lines = result.summary_lines()
    assert any("PORT" in l for l in lines)


def test_type_issue_str() -> None:
    issue = TypeIssue("PORT", "bad", "int", "cannot parse as integer")
    s = str(issue)
    assert "PORT" in s
    assert "int" in s
