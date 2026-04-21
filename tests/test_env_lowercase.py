"""Tests for envault.env_lowercase."""

from __future__ import annotations

from pathlib import Path

import pytest

from envault.env_lowercase import LowercaseError, _parse_lines, lowercase_env


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# _parse_lines unit tests
# ---------------------------------------------------------------------------

def test_parse_lines_already_lower():
    lines = _parse_lines("db_host=localhost\n")
    assert lines == [("db_host=localhost\n", False)]


def test_parse_lines_uppercase_key():
    lines = _parse_lines("DB_HOST=localhost\n")
    assert lines == [("db_host=localhost\n", True)]


def test_parse_lines_mixed_case():
    lines = _parse_lines("DbHost=localhost\n")
    assert lines == [("dbhost=localhost\n", True)]


def test_parse_lines_comment_unchanged():
    lines = _parse_lines("# This is a comment\n")
    assert lines == [("# This is a comment\n", False)]


def test_parse_lines_blank_line_unchanged():
    lines = _parse_lines("\n")
    assert lines == [("\n", False)]


def test_parse_lines_preserves_value_case():
    lines = _parse_lines("API_KEY=MySecretValue\n")
    text, changed = lines[0]
    assert text == "api_key=MySecretValue\n"
    assert changed is True


# ---------------------------------------------------------------------------
# lowercase_env integration tests
# ---------------------------------------------------------------------------

def test_lowercase_env_in_place(tmp_dir: Path):
    f = _write(tmp_dir / ".env", "DB_HOST=localhost\nAPI_KEY=secret\n")
    changed = lowercase_env(f)
    assert set(changed) == {"db_host", "api_key"}
    assert f.read_text() == "db_host=localhost\napi_key=secret\n"


def test_lowercase_env_already_lower_no_changes(tmp_dir: Path):
    f = _write(tmp_dir / ".env", "db_host=localhost\napi_key=secret\n")
    changed = lowercase_env(f)
    assert changed == []


def test_lowercase_env_to_separate_dest(tmp_dir: Path):
    src = _write(tmp_dir / ".env", "DB_HOST=localhost\n")
    dest = tmp_dir / ".env.lower"
    lowercase_env(src, dest)
    assert dest.read_text() == "db_host=localhost\n"
    # Source must be untouched
    assert src.read_text() == "DB_HOST=localhost\n"


def test_lowercase_env_dry_run_does_not_write(tmp_dir: Path):
    original = "DB_HOST=localhost\n"
    f = _write(tmp_dir / ".env", original)
    changed = lowercase_env(f, dry_run=True)
    assert changed == ["db_host"]
    assert f.read_text() == original  # untouched


def test_lowercase_env_missing_file_raises(tmp_dir: Path):
    with pytest.raises(LowercaseError, match="not found"):
        lowercase_env(tmp_dir / "nonexistent.env")


def test_lowercase_env_preserves_comments(tmp_dir: Path):
    content = "# section\nDB_HOST=localhost\n\nAPI_KEY=abc\n"
    f = _write(tmp_dir / ".env", content)
    changed = lowercase_env(f)
    assert set(changed) == {"db_host", "api_key"}
    assert f.read_text() == "# section\ndb_host=localhost\n\napi_key=abc\n"


def test_lowercase_env_dry_run_with_dest_does_not_create_dest(tmp_dir: Path):
    """When dry_run=True and a destination path is provided, the destination
    file should NOT be created."""
    src = _write(tmp_dir / ".env", "DB_HOST=localhost\n")
    dest = tmp_dir / ".env.lower"
    lowercase_env(src, dest, dry_run=True)
    assert not dest.exists()
