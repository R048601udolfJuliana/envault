"""Tests for envault.env_reorder."""

from __future__ import annotations

from pathlib import Path

import pytest

from envault.env_reorder import ReorderError, reorder_env


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content, encoding="utf-8")
    return p


def test_reorder_basic(tmp_dir: Path) -> None:
    src = _write(
        tmp_dir / ".env",
        "FOO=1\nBAR=2\nBAZ=3\n",
    )
    reorder_env(src, ["BAZ", "FOO", "BAR"])
    lines = [l for l in src.read_text().splitlines() if l.strip()]
    keys = [l.split("=")[0] for l in lines]
    assert keys == ["BAZ", "FOO", "BAR"]


def test_reorder_partial_order_appends_unmatched(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "A=1\nB=2\nC=3\n")
    reorder_env(src, ["C", "A"])
    lines = [l for l in src.read_text().splitlines() if l.strip()]
    keys = [l.split("=")[0] for l in lines]
    assert keys[0] == "C"
    assert keys[1] == "A"
    assert "B" in keys


def test_reorder_drop_unmatched(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "A=1\nB=2\nC=3\n")
    reorder_env(src, ["C", "A"], append_unmatched=False)
    text = src.read_text()
    assert "B" not in text
    assert "C=3" in text
    assert "A=1" in text


def test_reorder_to_separate_dest(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "X=10\nY=20\n")
    dest = tmp_dir / ".env.reordered"
    result = reorder_env(src, ["Y", "X"], dest=dest)
    assert result == dest.resolve()
    assert dest.exists()
    # Original unchanged
    assert src.read_text() == "X=10\nY=20\n"


def test_reorder_preserves_comments(tmp_dir: Path) -> None:
    src = _write(
        tmp_dir / ".env",
        "# comment for A\nA=1\n# comment for B\nB=2\n",
    )
    reorder_env(src, ["B", "A"])
    text = src.read_text()
    b_pos = text.index("B=2")
    a_pos = text.index("A=1")
    assert b_pos < a_pos
    assert "# comment for B" in text
    assert "# comment for A" in text


def test_reorder_missing_file_raises(tmp_dir: Path) -> None:
    with pytest.raises(ReorderError, match="not found"):
        reorder_env(tmp_dir / "missing.env", ["A"])


def test_reorder_empty_order_appends_all(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "A=1\nB=2\n")
    reorder_env(src, [])
    text = src.read_text()
    assert "A=1" in text
    assert "B=2" in text


def test_reorder_returns_resolved_dest(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "K=v\n")
    result = reorder_env(src, ["K"])
    assert result == src.resolve()
