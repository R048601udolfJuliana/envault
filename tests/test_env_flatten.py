"""Tests for envault.env_flatten."""
from pathlib import Path

import pytest

from envault.env_flatten import FlattenError, flatten_env


@pytest.fixture
def tmp_dir(tmp_path):
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content, encoding="utf-8")
    return p


def test_flatten_basic(tmp_dir):
    a = _write(tmp_dir / "a.env", "FOO=1\nBAR=2\n")
    b = _write(tmp_dir / "b.env", "BAZ=3\n")
    dest = tmp_dir / "out.env"
    result = flatten_env([a, b], dest)
    assert result == {"FOO": "1", "BAR": "2", "BAZ": "3"}
    assert dest.exists()


def test_flatten_last_wins(tmp_dir):
    a = _write(tmp_dir / "a.env", "FOO=original\n")
    b = _write(tmp_dir / "b.env", "FOO=override\n")
    dest = tmp_dir / "out.env"
    result = flatten_env([a, b], dest, last_wins=True)
    assert result["FOO"] == "override"


def test_flatten_first_wins(tmp_dir):
    a = _write(tmp_dir / "a.env", "FOO=original\n")
    b = _write(tmp_dir / "b.env", "FOO=override\n")
    dest = tmp_dir / "out.env"
    result = flatten_env([a, b], dest, last_wins=False)
    assert result["FOO"] == "original"


def test_flatten_missing_source_raises(tmp_dir):
    dest = tmp_dir / "out.env"
    with pytest.raises(FlattenError, match="not found"):
        flatten_env([tmp_dir / "missing.env"], dest)


def test_flatten_ignores_comments_and_blanks(tmp_dir):
    a = _write(tmp_dir / "a.env", "# comment\n\nFOO=1\n")
    dest = tmp_dir / "out.env"
    result = flatten_env([a], dest)
    assert list(result.keys()) == ["FOO"]


def test_flatten_comment_source_written(tmp_dir):
    a = _write(tmp_dir / "a.env", "FOO=1\n")
    dest = tmp_dir / "out.env"
    flatten_env([a], dest, comment_source=True)
    content = dest.read_text()
    assert "# source: a.env" in content


def test_flatten_dest_content_has_all_keys(tmp_dir):
    a = _write(tmp_dir / "a.env", "A=1\nB=2\n")
    b = _write(tmp_dir / "b.env", "C=3\n")
    dest = tmp_dir / "out.env"
    flatten_env([a, b], dest)
    content = dest.read_text()
    assert "A=1" in content
    assert "B=2" in content
    assert "C=3" in content


def test_flatten_strips_quoted_values(tmp_dir):
    a = _write(tmp_dir / "a.env", 'KEY="hello"\n')
    dest = tmp_dir / "out.env"
    result = flatten_env([a], dest)
    assert result["KEY"] == "hello"
