"""Tests for envault.env_diff_apply."""
from __future__ import annotations

import pytest
from pathlib import Path

from envault.env_diff_apply import ApplyError, apply_additions, apply_removals


@pytest.fixture
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(path: Path, content: str) -> None:
    path.write_text(content)


def test_apply_additions_adds_new_key(tmp_dir: Path) -> None:
    env = tmp_dir / ".env"
    _write(env, "FOO=bar\n")
    applied = apply_additions(env, {"BAZ": "qux"})
    assert "BAZ" in applied
    assert "BAZ=qux" in env.read_text()


def test_apply_additions_overwrites_existing(tmp_dir: Path) -> None:
    env = tmp_dir / ".env"
    _write(env, "FOO=old\nBAR=keep\n")
    applied = apply_additions(env, {"FOO": "new"})
    assert "FOO" in applied
    text = env.read_text()
    assert "FOO=new" in text
    assert "FOO=old" not in text
    assert "BAR=keep" in text


def test_apply_additions_preserves_comments(tmp_dir: Path) -> None:
    env = tmp_dir / ".env"
    _write(env, "# comment\nFOO=bar\n")
    apply_additions(env, {"NEW": "val"})
    text = env.read_text()
    assert "# comment" in text


def test_apply_additions_missing_file_raises(tmp_dir: Path) -> None:
    with pytest.raises(ApplyError):
        apply_additions(tmp_dir / "missing.env", {"K": "v"})


def test_apply_removals_removes_key(tmp_dir: Path) -> None:
    env = tmp_dir / ".env"
    _write(env, "FOO=bar\nBAZ=qux\n")
    removed = apply_removals(env, ["FOO"])
    assert "FOO" in removed
    text = env.read_text()
    assert "FOO" not in text
    assert "BAZ=qux" in text


def test_apply_removals_missing_key_not_in_result(tmp_dir: Path) -> None:
    env = tmp_dir / ".env"
    _write(env, "FOO=bar\n")
    removed = apply_removals(env, ["GHOST"])
    assert "GHOST" not in removed


def test_apply_removals_missing_file_raises(tmp_dir: Path) -> None:
    with pytest.raises(ApplyError):
        apply_removals(Path("/no/such/.env"), ["K"])


def test_apply_additions_multiple_keys(tmp_dir: Path) -> None:
    env = tmp_dir / ".env"
    _write(env, "")
    applied = apply_additions(env, {"A": "1", "B": "2"})
    assert set(applied) == {"A", "B"}
    text = env.read_text()
    assert "A=1" in text
    assert "B=2" in text
