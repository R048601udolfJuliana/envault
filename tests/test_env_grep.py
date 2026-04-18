"""Tests for envault.env_grep"""
from pathlib import Path
import pytest
from envault.env_grep import GrepError, GrepMatch, grep_env


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text(
        "# comment\n"
        "DATABASE_URL=postgres://localhost/mydb\n"
        "SECRET_KEY=supersecret\n"
        "DEBUG=true\n"
        "EMPTY_KEY=\n"
    )
    return p


def test_grep_returns_grep_result_type(env_file):
    result = grep_env(env_file, "DEBUG")
    assert result.found


def test_grep_matches_key(env_file):
    result = grep_env(env_file, "SECRET")
    assert len(result.matches) == 1
    assert result.matches[0].key == "SECRET_KEY"


def test_grep_matches_value(env_file):
    result = grep_env(env_file, "postgres")
    assert result.found
    assert result.matches[0].key == "DATABASE_URL"
    assert result.matches[0].matched_field == "value"


def test_grep_case_insensitive_by_default(env_file):
    result = grep_env(env_file, "supersecret")
    assert result.found


def test_grep_case_sensitive_flag(env_file):
    result = grep_env(env_file, "supersecret", case_sensitive=True)
    assert not result.found
    result2 = grep_env(env_file, "supersecret", case_sensitive=False)
    assert result2.found


def test_grep_keys_only(env_file):
    result = grep_env(env_file, "postgres", search_keys=True, search_values=False)
    assert not result.found


def test_grep_values_only(env_file):
    result = grep_env(env_file, "DATABASE", search_keys=False, search_values=True)
    assert not result.found


def test_grep_both_matched_field(env_file):
    # pattern matches both key and value
    result = grep_env(env_file, "true", search_keys=True, search_values=True)
    assert result.found


def test_grep_no_matches_returns_empty(env_file):
    result = grep_env(env_file, "ZZZNOMATCH")
    assert not result.found
    assert "No matches" in result.summary()


def test_grep_missing_file_raises(tmp_path):
    with pytest.raises(GrepError, match="not found"):
        grep_env(tmp_path / "missing.env", "KEY")


def test_grep_invalid_pattern_raises(env_file):
    with pytest.raises(GrepError, match="Invalid pattern"):
        grep_env(env_file, "[invalid")


def test_grep_neither_keys_nor_values_raises(env_file):
    with pytest.raises(GrepError):
        grep_env(env_file, "KEY", search_keys=False, search_values=False)


def test_grep_match_str(env_file):
    result = grep_env(env_file, "DEBUG")
    assert "DEBUG" in str(result.matches[0])
