"""Tests for envault.env_secret."""
from __future__ import annotations

from pathlib import Path

import pytest

from envault.env_secret import (
    SecretError,
    SecretMatch,
    SecretResult,
    _entropy,
    scan_secrets,
)


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content)
    return p


# --- unit: _entropy ---

def test_entropy_empty_string_is_zero():
    assert _entropy("") == 0.0


def test_entropy_uniform_string_is_high():
    # Random-looking string should have high entropy
    val = "aB3$xY9!qW2"
    assert _entropy(val) > 3.0


def test_entropy_repeated_char_is_low():
    assert _entropy("aaaaaaa") < 1.0


# --- SecretResult ---

def test_secret_result_no_matches_not_found():
    r = SecretResult(matches=[])
    assert not r.found


def test_secret_result_with_match_is_found():
    r = SecretResult(matches=[SecretMatch("TOKEN", "abc123", "sensitive key name")])
    assert r.found


def test_secret_result_summary_lines_no_matches():
    lines = SecretResult().summary_lines()
    assert lines == ["No secrets detected."]


def test_secret_result_summary_lines_with_matches():
    r = SecretResult(matches=[SecretMatch("API_KEY", "supersecret", "sensitive key name")])
    lines = r.summary_lines()
    assert lines[0].startswith("Detected 1")
    assert any("API_KEY" in l for l in lines)


# --- scan_secrets ---

def test_scan_secrets_missing_file_raises(tmp_dir: Path):
    with pytest.raises(SecretError, match="not found"):
        scan_secrets(tmp_dir / "missing.env")


def test_scan_detects_sensitive_key_name(tmp_dir: Path):
    f = _write(tmp_dir / ".env", "API_KEY=somevalue\n")
    result = scan_secrets(f, check_entropy=False)
    assert result.found
    assert result.matches[0].key == "API_KEY"
    assert "sensitive key name" in result.matches[0].reason


def test_scan_detects_high_entropy_value(tmp_dir: Path):
    f = _write(tmp_dir / ".env", "RANDOM_THING=aB3xY9qW2zK8mN5p\n")
    result = scan_secrets(f, check_names=False)
    assert result.found
    assert "entropy" in result.matches[0].reason


def test_scan_ignores_empty_values(tmp_dir: Path):
    f = _write(tmp_dir / ".env", "PASSWORD=\n")
    result = scan_secrets(f)
    assert not result.found


def test_scan_ignores_comments_and_blanks(tmp_dir: Path):
    f = _write(tmp_dir / ".env", "# comment\n\nHOST=localhost\n")
    result = scan_secrets(f)
    assert not result.found


def test_scan_no_entropy_flag_skips_entropy(tmp_dir: Path):
    f = _write(tmp_dir / ".env", "RANDOM_THING=aB3xY9qW2zK8mN5p\n")
    result = scan_secrets(f, check_entropy=False, check_names=False)
    assert not result.found


def test_secret_match_str_masks_value():
    m = SecretMatch("TOKEN", "supersecret", "sensitive key name")
    s = str(m)
    assert "su***" in s
    assert "supersecret" not in s
