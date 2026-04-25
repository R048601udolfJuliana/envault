"""Tests for envault.env_required."""
from __future__ import annotations

import pytest
from pathlib import Path

from envault.env_required import (
    MissingKey,
    RequiredError,
    RequiredResult,
    check_required,
)


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, text: str) -> Path:
    p.write_text(text, encoding="utf-8")
    return p


# --- RequiredResult ---

def test_required_result_ok_when_no_missing():
    r = RequiredResult()
    assert r.ok is True


def test_required_result_not_ok_when_missing():
    r = RequiredResult(missing=[MissingKey(key="FOO", reason="absent")])
    assert r.ok is False


def test_required_result_summary_lines_ok():
    r = RequiredResult()
    lines = r.summary_lines()
    assert len(lines) == 1
    assert "present" in lines[0]


def test_required_result_summary_lines_missing():
    r = RequiredResult(missing=[MissingKey("BAR", "absent"), MissingKey("BAZ", "empty")])
    lines = r.summary_lines()
    assert any("BAR" in l for l in lines)
    assert any("BAZ" in l for l in lines)


# --- check_required ---

def test_check_required_all_present(tmp_dir: Path):
    f = _write(tmp_dir / ".env", "FOO=bar\nBAZ=qux\n")
    result = check_required(f, ["FOO", "BAZ"])
    assert result.ok


def test_check_required_absent_key(tmp_dir: Path):
    f = _write(tmp_dir / ".env", "FOO=bar\n")
    result = check_required(f, ["FOO", "MISSING"])
    assert not result.ok
    assert any(m.key == "MISSING" and m.reason == "absent" for m in result.missing)


def test_check_required_empty_value_flagged(tmp_dir: Path):
    f = _write(tmp_dir / ".env", "FOO=\n")
    result = check_required(f, ["FOO"])
    assert not result.ok
    assert result.missing[0].reason == "empty"


def test_check_required_allow_empty_passes(tmp_dir: Path):
    f = _write(tmp_dir / ".env", "FOO=\n")
    result = check_required(f, ["FOO"], allow_empty=True)
    assert result.ok


def test_check_required_strips_quotes(tmp_dir: Path):
    f = _write(tmp_dir / ".env", 'FOO="hello"\n')
    result = check_required(f, ["FOO"])
    assert result.ok


def test_check_required_missing_file_raises(tmp_dir: Path):
    with pytest.raises(RequiredError, match="not found"):
        check_required(tmp_dir / "nonexistent.env", ["FOO"])


def test_check_required_no_keys_returns_ok(tmp_dir: Path):
    f = _write(tmp_dir / ".env", "FOO=bar\n")
    result = check_required(f, [])
    assert result.ok


def test_missing_key_str():
    m = MissingKey(key="API_KEY", reason="absent")
    assert "API_KEY" in str(m)
    assert "absent" in str(m)
