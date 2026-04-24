"""Tests for envault.env_whitelist."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.env_whitelist import WhitelistError, whitelist_env, _key_of


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# _key_of
# ---------------------------------------------------------------------------

def test_key_of_basic():
    assert _key_of("FOO=bar\n") == "FOO"


def test_key_of_comment_returns_none():
    assert _key_of("# comment\n") is None


def test_key_of_blank_returns_none():
    assert _key_of("   \n") is None


def test_key_of_no_equals_returns_none():
    assert _key_of("NOEQUALS\n") is None


# ---------------------------------------------------------------------------
# whitelist_env
# ---------------------------------------------------------------------------

def test_whitelist_keeps_allowed_keys(tmp_dir: Path):
    src = _write(tmp_dir / ".env", "FOO=1\nBAR=2\nBAZ=3\n")
    whitelist_env(src, ["FOO", "BAZ"])
    result = src.read_text()
    assert "FOO=1" in result
    assert "BAZ=3" in result
    assert "BAR" not in result


def test_whitelist_removes_unlisted_keys(tmp_dir: Path):
    src = _write(tmp_dir / ".env", "SECRET=x\nPUBLIC=y\n")
    whitelist_env(src, ["PUBLIC"])
    assert "SECRET" not in src.read_text()


def test_whitelist_preserves_comments_by_default(tmp_dir: Path):
    src = _write(tmp_dir / ".env", "# header\nFOO=1\nBAR=2\n")
    whitelist_env(src, ["FOO"])
    assert "# header" in src.read_text()


def test_whitelist_strip_comments_flag(tmp_dir: Path):
    src = _write(tmp_dir / ".env", "# header\nFOO=1\nBAR=2\n")
    whitelist_env(src, ["FOO"], keep_comments=False)
    text = src.read_text()
    assert "# header" not in text
    assert "FOO=1" in text


def test_whitelist_writes_to_dest(tmp_dir: Path):
    src = _write(tmp_dir / ".env", "A=1\nB=2\n")
    dest = tmp_dir / ".env.filtered"
    whitelist_env(src, ["A"], dest=dest)
    assert dest.exists()
    assert "A=1" in dest.read_text()
    # src unchanged
    assert "B=2" in src.read_text()


def test_whitelist_returns_resolved_path(tmp_dir: Path):
    src = _write(tmp_dir / ".env", "X=1\n")
    result = whitelist_env(src, ["X"])
    assert result == src.resolve()


def test_whitelist_missing_file_raises(tmp_dir: Path):
    with pytest.raises(WhitelistError, match="not found"):
        whitelist_env(tmp_dir / "missing.env", ["FOO"])


def test_whitelist_empty_keys_raises(tmp_dir: Path):
    src = _write(tmp_dir / ".env", "FOO=1\n")
    with pytest.raises(WhitelistError, match="empty"):
        whitelist_env(src, [])


def test_whitelist_all_keys_removed_leaves_empty(tmp_dir: Path):
    src = _write(tmp_dir / ".env", "FOO=1\nBAR=2\n")
    whitelist_env(src, ["NONEXISTENT"], keep_comments=False)
    assert src.read_text().strip() == ""
