"""Tests for envault.env_inherit."""
from __future__ import annotations

from pathlib import Path

import pytest

from envault.env_inherit import InheritError, inherit_env


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content, encoding="utf-8")
    return p


def test_inherit_adds_missing_keys(tmp_dir: Path) -> None:
    parent = _write(tmp_dir / "parent.env", "BASE_URL=https://example.com\nDEBUG=false\n")
    child = _write(tmp_dir / "child.env", "APP_NAME=myapp\nDEBUG=true\n")

    out, inherited = inherit_env(parent, child)

    assert out == child
    assert inherited == ["BASE_URL"]
    text = child.read_text()
    assert "BASE_URL=https://example.com" in text
    # child DEBUG should not be overwritten
    assert "DEBUG=true" in text


def test_inherit_no_new_keys(tmp_dir: Path) -> None:
    parent = _write(tmp_dir / "parent.env", "KEY=val\n")
    child = _write(tmp_dir / "child.env", "KEY=override\n")

    _, inherited = inherit_env(parent, child)

    assert inherited == []
    assert "KEY=override" in child.read_text()


def test_inherit_writes_to_dest(tmp_dir: Path) -> None:
    parent = _write(tmp_dir / "parent.env", "SHARED=1\n")
    child = _write(tmp_dir / "child.env", "OWN=2\n")
    dest = tmp_dir / "merged.env"

    out, inherited = inherit_env(parent, child, dest=dest)

    assert out == dest
    assert dest.exists()
    assert "SHARED=1" in dest.read_text()
    # original child should be untouched
    assert "SHARED" not in child.read_text()


def test_inherit_show_source_adds_comment(tmp_dir: Path) -> None:
    parent = _write(tmp_dir / "parent.env", "TOKEN=abc\n")
    child = _write(tmp_dir / "child.env", "APP=x\n")

    _, _ = inherit_env(parent, child, show_source=True)

    text = child.read_text()
    assert "# inherited from" in text


def test_inherit_missing_parent_raises(tmp_dir: Path) -> None:
    child = _write(tmp_dir / "child.env", "X=1\n")
    with pytest.raises(InheritError, match="Parent file not found"):
        inherit_env(tmp_dir / "ghost.env", child)


def test_inherit_missing_child_raises(tmp_dir: Path) -> None:
    parent = _write(tmp_dir / "parent.env", "X=1\n")
    with pytest.raises(InheritError, match="Child file not found"):
        inherit_env(parent, tmp_dir / "ghost.env")


def test_inherit_strips_quotes_from_parent(tmp_dir: Path) -> None:
    parent = _write(tmp_dir / "parent.env", 'URL="https://api.example.com"\n')
    child = _write(tmp_dir / "child.env", "APP=demo\n")

    _, inherited = inherit_env(parent, child)

    assert "URL" in inherited
    text = child.read_text()
    assert "URL=https://api.example.com" in text
