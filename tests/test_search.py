"""Tests for envault.search."""

from __future__ import annotations

from pathlib import Path

import pytest

from envault.search import SearchError, SearchMatch, SearchResult, search_env


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        "DB_HOST=localhost\n"
        "DB_PORT=5432\n"
        "# a comment\n"
        "\n"
        "API_KEY=secret123\n"
        "APP_DEBUG=true\n",
        encoding="utf-8",
    )
    return p


def test_search_returns_result_type(env_file: Path) -> None:
    result = search_env(env_file, "DB")
    assert isinstance(result, SearchResult)


def test_search_matches_key_prefix(env_file: Path) -> None:
    result = search_env(env_file, "^DB_")
    assert result.found
    keys = [m.key for m in result.matches]
    assert "DB_HOST" in keys
    assert "DB_PORT" in keys
    assert "API_KEY" not in keys


def test_search_case_insensitive_by_default(env_file: Path) -> None:
    result = search_env(env_file, "db_host")
    assert result.found
    assert result.matches[0].key == "DB_HOST"


def test_search_case_sensitive_flag(env_file: Path) -> None:
    result = search_env(env_file, "db_host", case_sensitive=True)
    assert not result.found


def test_search_no_match_returns_empty(env_file: Path) -> None:
    result = search_env(env_file, "NONEXISTENT")
    assert not result.found
    assert result.matches == []


def test_search_values_flag(env_file: Path) -> None:
    result = search_env(env_file, "secret", search_values=True)
    assert result.found
    assert result.matches[0].key == "API_KEY"


def test_search_values_flag_off_by_default(env_file: Path) -> None:
    result = search_env(env_file, "secret")
    assert not result.found


def test_search_match_line_number(env_file: Path) -> None:
    result = search_env(env_file, "^API_KEY$")
    assert result.found
    assert result.matches[0].line_number == 5


def test_search_match_str(env_file: Path) -> None:
    result = search_env(env_file, "^DB_HOST$")
    assert "DB_HOST=localhost" in str(result.matches[0])


def test_summary_with_matches(env_file: Path) -> None:
    result = search_env(env_file, "DB")
    summary = result.summary()
    assert "match" in summary
    assert "DB" in summary


def test_summary_no_matches(env_file: Path) -> None:
    result = search_env(env_file, "NOTHING")
    assert "No matches" in result.summary()


def test_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(SearchError, match="File not found"):
        search_env(tmp_path / "missing.env", "KEY")


def test_invalid_pattern_raises(env_file: Path) -> None:
    with pytest.raises(SearchError, match="Invalid pattern"):
        search_env(env_file, "[invalid")
