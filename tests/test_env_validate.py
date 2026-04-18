"""Tests for envault.env_validate"""
import pytest
from pathlib import Path

from envault.env_validate import ValidateError, ValidationIssue, ValidationResult, validate_env


@pytest.fixture
def tmp_dir(tmp_path):
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content)
    return p


def test_validate_all_present(tmp_dir):
    f = _write(tmp_dir / ".env", "DB_HOST=localhost\nDB_PORT=5432\n")
    result = validate_env(f, ["DB_HOST", "DB_PORT"])
    assert result.ok


def test_validate_missing_key(tmp_dir):
    f = _write(tmp_dir / ".env", "DB_HOST=localhost\n")
    result = validate_env(f, ["DB_HOST", "DB_PORT"])
    assert not result.ok
    assert any(i.key == "DB_PORT" for i in result.issues)


def test_validate_empty_value(tmp_dir):
    f = _write(tmp_dir / ".env", "SECRET=\n")
    result = validate_env(f, ["SECRET"])
    assert not result.ok
    assert result.issues[0].message == "value is empty"


def test_validate_pattern_passes(tmp_dir):
    f = _write(tmp_dir / ".env", "PORT=8080\n")
    result = validate_env(f, ["PORT"], {"PORT": r"\d+"})
    assert result.ok


def test_validate_pattern_fails(tmp_dir):
    f = _write(tmp_dir / ".env", "PORT=abc\n")
    result = validate_env(f, ["PORT"], {"PORT": r"\d+"})
    assert not result.ok
    assert "pattern" in result.issues[0].message


def test_validate_missing_file_raises(tmp_dir):
    with pytest.raises(ValidateError, match="not found"):
        validate_env(tmp_dir / "missing.env", ["KEY"])


def test_summary_ok(tmp_dir):
    f = _write(tmp_dir / ".env", "A=1\n")
    result = validate_env(f, ["A"])
    assert "All required" in result.summary()


def test_summary_with_issues(tmp_dir):
    f = _write(tmp_dir / ".env", "")
    result = validate_env(f, ["A", "B"])
    summary = result.summary()
    assert "A" in summary
    assert "B" in summary


def test_validation_issue_str():
    issue = ValidationIssue(key="FOO", message="missing required key")
    assert str(issue) == "FOO: missing required key"
