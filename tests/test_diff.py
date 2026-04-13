"""Tests for envault.diff."""
from pathlib import Path

import pytest

from envault.diff import DiffError, EnvDiff, diff_env_files, unified_diff, _parse_env


@pytest.fixture
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


def test_parse_env_basic():
    text = "FOO=bar\nBAZ=qux\n"
    assert _parse_env(text) == {"FOO": "bar", "BAZ": "qux"}


def test_parse_env_ignores_comments_and_blanks():
    text = "# comment\n\nFOO=bar\n"
    assert _parse_env(text) == {"FOO": "bar"}


def test_parse_env_no_value_line_skipped():
    text = "INVALID_LINE\nFOO=bar\n"
    assert _parse_env(text) == {"FOO": "bar"}


def test_diff_env_files_no_changes(tmp_dir):
    a = _write(tmp_dir / "a.env", "FOO=1\nBAR=2\n")
    b = _write(tmp_dir / "b.env", "FOO=1\nBAR=2\n")
    result = diff_env_files(a, b)
    assert not result.has_changes
    assert result.summary() == "No changes."


def test_diff_env_files_added_key(tmp_dir):
    a = _write(tmp_dir / "a.env", "FOO=1\n")
    b = _write(tmp_dir / "b.env", "FOO=1\nBAR=2\n")
    result = diff_env_files(a, b)
    assert result.added == ["BAR"]
    assert result.removed == []
    assert result.changed == []
    assert result.has_changes


def test_diff_env_files_removed_key(tmp_dir):
    a = _write(tmp_dir / "a.env", "FOO=1\nBAR=2\n")
    b = _write(tmp_dir / "b.env", "FOO=1\n")
    result = diff_env_files(a, b)
    assert result.removed == ["BAR"]
    assert result.added == []


def test_diff_env_files_changed_value(tmp_dir):
    a = _write(tmp_dir / "a.env", "FOO=old\n")
    b = _write(tmp_dir / "b.env", "FOO=new\n")
    result = diff_env_files(a, b)
    assert result.changed == [("FOO", "old", "new")]
    assert "FOO" in result.summary()


def test_diff_env_files_missing_file_raises(tmp_dir):
    a = tmp_dir / "missing.env"
    b = _write(tmp_dir / "b.env", "FOO=1\n")
    with pytest.raises(DiffError, match="not found"):
        diff_env_files(a, b)


def test_unified_diff_returns_string(tmp_dir):
    a = _write(tmp_dir / "a.env", "FOO=1\n")
    b = _write(tmp_dir / "b.env", "FOO=2\n")
    result = unified_diff(a, b)
    assert isinstance(result, str)
    assert "-FOO=1" in result
    assert "+FOO=2" in result


def test_unified_diff_missing_file_raises(tmp_dir):
    a = tmp_dir / "nope.env"
    b = _write(tmp_dir / "b.env", "FOO=1\n")
    with pytest.raises(DiffError):
        unified_diff(a, b)


def test_env_diff_summary_all_types():
    d = EnvDiff(added=["NEW"], removed=["OLD"], changed=[("MOD", "v1", "v2")])
    summary = d.summary()
    assert "+ NEW" in summary
    assert "- OLD" in summary
    assert "~ MOD" in summary
