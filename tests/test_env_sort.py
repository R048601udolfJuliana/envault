"""Tests for envault.env_sort."""
from __future__ import annotations

import pytest
from pathlib import Path

from envault.env_sort import SortError, sort_env


@pytest.fixture
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content)
    return p


def test_sort_basic(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "ZEBRA=1\nAPPLE=2\nMANGO=3\n")
    sort_env(f)
    lines = [l for l in f.read_text().splitlines() if l.strip()]
    assert lines == ["APPLE=2", "MANGO=3", "ZEBRA=1"]


def test_sort_reverse(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "APPLE=2\nZEBRA=1\nMANGO=3\n")
    sort_env(f, reverse=True)
    lines = [l for l in f.read_text().splitlines() if l.strip()]
    assert lines == ["ZEBRA=1", "MANGO=3", "APPLE=2"]


def test_sort_to_separate_dest(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "Z=1\nA=2\n")
    dest = tmp_dir / "sorted.env"
    sort_env(src, dest)
    assert dest.exists()
    lines = [l for l in dest.read_text().splitlines() if l.strip()]
    assert lines[0].startswith("A=")


def test_sort_preserves_inline_comments(tmp_dir: Path) -> None:
    content = "# header\nZEBRA=1\nAPPLE=2\n"
    f = _write(tmp_dir / ".env", content)
    sort_env(f)
    text = f.read_text()
    assert "APPLE" in text
    assert text.index("APPLE") < text.index("ZEBRA")


def test_sort_missing_file_raises(tmp_dir: Path) -> None:
    with pytest.raises(SortError, match="not found"):
        sort_env(tmp_dir / "missing.env")


def test_sort_empty_file(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "")
    sort_env(f)
    assert f.read_text() == ""


def test_sort_returns_resolved_path(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "B=1\nA=2\n")
    result = sort_env(f)
    assert result == f.resolve()
