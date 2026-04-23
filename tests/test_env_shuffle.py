"""Tests for envault.env_shuffle."""

from __future__ import annotations

from pathlib import Path

import pytest

from envault.env_shuffle import ShuffleError, _parse_blocks, shuffle_env


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# _parse_blocks
# ---------------------------------------------------------------------------

def test_parse_blocks_groups_comment_with_key(tmp_dir: Path) -> None:
    blocks = _parse_blocks("# comment\nFOO=bar\n")
    assert any("FOO=bar\n" in "".join(b) for b in blocks)


def test_parse_blocks_blank_lines_are_own_block(tmp_dir: Path) -> None:
    blocks = _parse_blocks("FOO=1\n\nBAR=2\n")
    # blank line becomes its own block
    blank_blocks = [b for b in blocks if b == ["\n"]]
    assert blank_blocks


# ---------------------------------------------------------------------------
# shuffle_env
# ---------------------------------------------------------------------------

def test_shuffle_env_creates_default_dest(tmp_dir: Path) -> None:
    src = _write(tmp_dir / "test.env", "A=1\nB=2\nC=3\n")
    result = shuffle_env(src)
    assert result.exists()
    assert result.name == "test.shuffled.env"


def test_shuffle_env_contains_all_keys(tmp_dir: Path) -> None:
    src = _write(tmp_dir / "test.env", "A=1\nB=2\nC=3\n")
    result = shuffle_env(src, seed=42)
    content = result.read_text()
    assert "A=1" in content
    assert "B=2" in content
    assert "C=3" in content


def test_shuffle_env_seed_is_reproducible(tmp_dir: Path) -> None:
    src = _write(tmp_dir / "test.env", "A=1\nB=2\nC=3\nD=4\nE=5\n")
    dest1 = tmp_dir / "out1.env"
    dest2 = tmp_dir / "out2.env"
    shuffle_env(src, dest=dest1, seed=99)
    shuffle_env(src, dest=dest2, seed=99)
    assert dest1.read_text() == dest2.read_text()


def test_shuffle_env_different_seeds_differ(tmp_dir: Path) -> None:
    src = _write(tmp_dir / "test.env", "A=1\nB=2\nC=3\nD=4\nE=5\n")
    dest1 = tmp_dir / "out1.env"
    dest2 = tmp_dir / "out2.env"
    shuffle_env(src, dest=dest1, seed=1)
    shuffle_env(src, dest=dest2, seed=2)
    # With 5 keys, the probability both orderings are identical is 1/120
    assert dest1.read_text() != dest2.read_text()


def test_shuffle_env_in_place(tmp_dir: Path) -> None:
    src = _write(tmp_dir / "test.env", "A=1\nB=2\nC=3\n")
    result = shuffle_env(src, in_place=True, seed=7)
    assert result == src.resolve()
    content = src.read_text()
    assert "A=1" in content and "B=2" in content and "C=3" in content


def test_shuffle_env_custom_dest(tmp_dir: Path) -> None:
    src = _write(tmp_dir / "test.env", "X=10\nY=20\n")
    dest = tmp_dir / "custom_output.env"
    result = shuffle_env(src, dest=dest, seed=0)
    assert result == dest.resolve()
    assert dest.exists()


def test_shuffle_env_missing_file_raises(tmp_dir: Path) -> None:
    with pytest.raises(ShuffleError, match="not found"):
        shuffle_env(tmp_dir / "nonexistent.env")


def test_shuffle_env_output_ends_with_newline(tmp_dir: Path) -> None:
    src = _write(tmp_dir / "test.env", "A=1\nB=2\n")
    result = shuffle_env(src, seed=3)
    assert result.read_text().endswith("\n")
