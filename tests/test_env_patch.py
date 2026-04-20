"""Tests for envault.env_patch."""
from __future__ import annotations

from pathlib import Path

import pytest

from envault.env_patch import PatchError, patch_env


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def test_patch_updates_existing_key(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "DB_HOST=localhost\nDB_PORT=5432\n")
    patch_env(f, {"DB_HOST": "prod.example.com"})
    lines = f.read_text().splitlines()
    assert "DB_HOST=prod.example.com" in lines
    assert "DB_PORT=5432" in lines


def test_patch_appends_missing_key(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "FOO=bar\n")
    patch_env(f, {"NEW_KEY": "new_value"})
    text = f.read_text()
    assert "NEW_KEY=new_value" in text
    assert "FOO=bar" in text


def test_patch_no_add_does_not_append(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "FOO=bar\n")
    patch_env(f, {"MISSING": "x"}, add_missing=False)
    text = f.read_text()
    assert "MISSING" not in text


def test_patch_preserves_comments(tmp_dir: Path) -> None:
    content = "# database config\nDB=sqlite\n"
    f = _write(tmp_dir / ".env", content)
    patch_env(f, {"DB": "postgres"})
    text = f.read_text()
    assert "# database config" in text
    assert "DB=postgres" in text


def test_patch_writes_to_dest(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "KEY=old\n")
    dest = tmp_dir / ".env.patched"
    result = patch_env(src, {"KEY": "new"}, dest=dest)
    assert result == dest
    assert dest.read_text().strip() == "KEY=new"
    assert src.read_text().strip() == "KEY=old"  # source unchanged


def test_patch_returns_dest_path(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "A=1\n")
    result = patch_env(f, {"A": "2"})
    assert result == f


def test_patch_missing_source_raises(tmp_dir: Path) -> None:
    with pytest.raises(PatchError, match="not found"):
        patch_env(tmp_dir / "nonexistent.env", {"K": "v"})


def test_patch_empty_overrides_raises(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "A=1\n")
    with pytest.raises(PatchError, match="No overrides"):
        patch_env(f, {})


def test_patch_multiple_keys(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "A=1\nB=2\nC=3\n")
    patch_env(f, {"A": "10", "C": "30"})
    lines = f.read_text().splitlines()
    assert "A=10" in lines
    assert "B=2" in lines
    assert "C=30" in lines
