"""Tests for envault.env_chunk."""
from __future__ import annotations

from pathlib import Path

import pytest

from envault.env_chunk import ChunkError, chunk_env


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, text: str) -> Path:
    p.write_text(text, encoding="utf-8")
    return p


def test_chunk_basic(tmp_dir: Path) -> None:
    src = _write(
        tmp_dir / ".env",
        "A=1\nB=2\nC=3\nD=4\n",
    )
    paths = chunk_env(src, n=2, dest_dir=tmp_dir / "out")
    assert len(paths) == 2
    content_0 = paths[0].read_text(encoding="utf-8").strip().splitlines()
    content_1 = paths[1].read_text(encoding="utf-8").strip().splitlines()
    assert content_0 == ["A=1", "B=2"]
    assert content_1 == ["C=3", "D=4"]


def test_chunk_creates_dest_dir(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "X=1\nY=2\n")
    dest = tmp_dir / "new_dir" / "sub"
    chunk_env(src, n=1, dest_dir=dest)
    assert dest.is_dir()


def test_chunk_custom_prefix(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "K=v\n")
    paths = chunk_env(src, n=1, dest_dir=tmp_dir / "out", prefix="part")
    assert paths[0].name == "part_01.env"


def test_chunk_ignores_comments_and_blanks(tmp_dir: Path) -> None:
    src = _write(
        tmp_dir / ".env",
        "# comment\n\nA=1\n\n# another\nB=2\n",
    )
    paths = chunk_env(src, n=1, dest_dir=tmp_dir / "out")
    lines = paths[0].read_text(encoding="utf-8").strip().splitlines()
    assert lines == ["A=1", "B=2"]


def test_chunk_n_greater_than_entries(tmp_dir: Path) -> None:
    """When n > number of entries each chunk gets at most 1 entry."""
    src = _write(tmp_dir / ".env", "A=1\nB=2\n")
    paths = chunk_env(src, n=5, dest_dir=tmp_dir / "out")
    assert len(paths) == 2  # only 2 entries available


def test_chunk_missing_source_raises(tmp_dir: Path) -> None:
    with pytest.raises(ChunkError, match="not found"):
        chunk_env(tmp_dir / "missing.env", n=2, dest_dir=tmp_dir / "out")


def test_chunk_n_zero_raises(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "A=1\n")
    with pytest.raises(ChunkError, match=">= 1"):
        chunk_env(src, n=0, dest_dir=tmp_dir / "out")


def test_chunk_empty_file_raises(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "# only comments\n\n")
    with pytest.raises(ChunkError, match="No key=value"):
        chunk_env(src, n=2, dest_dir=tmp_dir / "out")
