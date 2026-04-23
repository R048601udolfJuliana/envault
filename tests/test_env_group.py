"""Tests for envault.env_group."""
from __future__ import annotations

from pathlib import Path

import pytest

from envault.env_group import GroupError, group_env


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content, encoding="utf-8")
    return p


def test_group_basic(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "DB_HOST=localhost\nDB_PORT=5432\nAWS_KEY=abc\n")
    dest = tmp_dir / "out.env"
    result = group_env(src, dest)
    assert "AWS" in result
    assert "DB" in result
    assert "DB_HOST" in result["DB"]
    assert "DB_PORT" in result["DB"]
    assert "AWS_KEY" in result["AWS"]


def test_group_no_separator_goes_to_other(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "PORT=8080\nDB_HOST=localhost\n")
    dest = tmp_dir / "out.env"
    result = group_env(src, dest)
    assert "OTHER" in result
    assert "PORT" in result["OTHER"]


def test_group_output_contains_section_headers(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "DB_HOST=localhost\nDB_PORT=5432\n")
    dest = tmp_dir / "out.env"
    group_env(src, dest)
    content = dest.read_text(encoding="utf-8")
    assert "# --- DB ---" in content
    assert "DB_HOST=localhost" in content


def test_group_min_group_size_merges_small_groups(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "DB_HOST=localhost\nAWS_KEY=abc\nAWS_SECRET=xyz\n")
    dest = tmp_dir / "out.env"
    # DB has only 1 member; with min_group_size=2 it should go to OTHER
    result = group_env(src, dest, min_group_size=2)
    assert "OTHER" in result
    assert "DB_HOST" in result["OTHER"]
    assert "AWS" in result


def test_group_missing_src_raises(tmp_dir: Path) -> None:
    with pytest.raises(GroupError, match="not found"):
        group_env(tmp_dir / "missing.env", tmp_dir / "out.env")


def test_group_ignores_comments_and_blanks(tmp_dir: Path) -> None:
    src = _write(
        tmp_dir / ".env",
        "# comment\n\nDB_HOST=localhost\nDB_PORT=5432\n",
    )
    dest = tmp_dir / "out.env"
    result = group_env(src, dest)
    all_keys = [k for keys in result.values() for k in keys]
    assert "DB_HOST" in all_keys
    assert "DB_PORT" in all_keys
    assert len(all_keys) == 2


def test_group_custom_separator(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "DB.HOST=localhost\nDB.PORT=5432\n")
    dest = tmp_dir / "out.env"
    result = group_env(src, dest, separator=".")
    assert "DB" in result
    assert len(result["DB"]) == 2
