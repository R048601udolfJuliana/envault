"""Tests for envault.env_join."""
from __future__ import annotations

from pathlib import Path

import pytest

from envault.env_join import JoinError, join_env


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


# ---------------------------------------------------------------------------
# Basic merging
# ---------------------------------------------------------------------------

def test_join_basic_last_wins(tmp_dir: Path) -> None:
    a = _write(tmp_dir / "a.env", "FOO=alpha\nBAR=1\n")
    b = _write(tmp_dir / "b.env", "FOO=beta\nBAZ=2\n")
    dest = tmp_dir / "out.env"
    join_env([a, b], dest)
    text = dest.read_text()
    assert "FOO=beta\n" in text
    assert "BAR=1\n" in text
    assert "BAZ=2\n" in text


def test_join_first_wins(tmp_dir: Path) -> None:
    a = _write(tmp_dir / "a.env", "FOO=alpha\n")
    b = _write(tmp_dir / "b.env", "FOO=beta\n")
    dest = tmp_dir / "out.env"
    join_env([a, b], dest, strategy="first")
    assert "FOO=alpha\n" in dest.read_text()


def test_join_returns_resolved_path(tmp_dir: Path) -> None:
    a = _write(tmp_dir / "a.env", "X=1\n")
    dest = tmp_dir / "out.env"
    result = join_env([a], dest)
    assert result == dest.resolve()


# ---------------------------------------------------------------------------
# Missing source files
# ---------------------------------------------------------------------------

def test_join_missing_source_raises(tmp_dir: Path) -> None:
    missing = tmp_dir / "nope.env"
    dest = tmp_dir / "out.env"
    with pytest.raises(JoinError, match="Source file not found"):
        join_env([missing], dest)


def test_join_skip_missing(tmp_dir: Path) -> None:
    a = _write(tmp_dir / "a.env", "KEY=val\n")
    missing = tmp_dir / "nope.env"
    dest = tmp_dir / "out.env"
    join_env([a, missing], dest, skip_missing=True)
    assert "KEY=val\n" in dest.read_text()


def test_join_all_missing_skip_writes_empty(tmp_dir: Path) -> None:
    dest = tmp_dir / "out.env"
    join_env([tmp_dir / "nope.env"], dest, skip_missing=True)
    assert dest.read_text() == ""


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_join_invalid_strategy_raises(tmp_dir: Path) -> None:
    a = _write(tmp_dir / "a.env", "A=1\n")
    dest = tmp_dir / "out.env"
    with pytest.raises(JoinError, match="Unknown strategy"):
        join_env([a], dest, strategy="random")


def test_join_preserves_key_order(tmp_dir: Path) -> None:
    a = _write(tmp_dir / "a.env", "ALPHA=1\nBETA=2\n")
    b = _write(tmp_dir / "b.env", "GAMMA=3\n")
    dest = tmp_dir / "out.env"
    join_env([a, b], dest)
    text = dest.read_text()
    assert text.index("ALPHA") < text.index("BETA") < text.index("GAMMA")


def test_join_trailing_newline_ensured(tmp_dir: Path) -> None:
    a = _write(tmp_dir / "a.env", "KEY=value")
    dest = tmp_dir / "out.env"
    join_env([a], dest)
    assert dest.read_text().endswith("\n")
