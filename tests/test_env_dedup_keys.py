"""Tests for envault.env_dedup_keys."""
from pathlib import Path

import pytest

from envault.env_dedup_keys import (
    DedupKeysError,
    _parse_env,
    find_cross_file_duplicates,
    dedup_keys,
)


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


# ── _parse_env ────────────────────────────────────────────────────────────────

def test_parse_env_basic():
    lines = _parse_env("FOO=bar\nBAZ=qux\n")
    assert [(1, "FOO", "FOO=bar"), (2, "BAZ", "BAZ=qux")] == lines


def test_parse_env_ignores_comments_and_blanks():
    text = "# comment\n\nFOO=1\n"
    result = _parse_env(text)
    assert len(result) == 1
    assert result[0][1] == "FOO"


def test_parse_env_skips_lines_without_equals():
    result = _parse_env("NOEQUALS\nFOO=bar\n")
    assert len(result) == 1


# ── find_cross_file_duplicates ────────────────────────────────────────────────

def test_find_cross_file_duplicates_detects_shared_key(tmp_dir: Path):
    a = _write(tmp_dir / "a.env", "FOO=1\nBAR=2\n")
    b = _write(tmp_dir / "b.env", "FOO=10\nBAZ=3\n")
    dupes = find_cross_file_duplicates([a, b])
    assert "FOO" in dupes
    assert len(dupes["FOO"]) == 2


def test_find_cross_file_duplicates_no_overlap(tmp_dir: Path):
    a = _write(tmp_dir / "a.env", "FOO=1\n")
    b = _write(tmp_dir / "b.env", "BAR=2\n")
    dupes = find_cross_file_duplicates([a, b])
    assert dupes == {}


def test_find_cross_file_duplicates_missing_file_raises(tmp_dir: Path):
    missing = tmp_dir / "missing.env"
    with pytest.raises(DedupKeysError, match="not found"):
        find_cross_file_duplicates([missing])


# ── dedup_keys ────────────────────────────────────────────────────────────────

def test_dedup_keys_removes_reference_keys(tmp_dir: Path):
    src = _write(tmp_dir / "src.env", "FOO=old\nBAR=keep\n")
    ref = _write(tmp_dir / "ref.env", "FOO=new\n")
    dedup_keys(src, ref, keep="reference")
    result = src.read_text()
    assert "FOO" not in result
    assert "BAR" in result


def test_dedup_keys_keep_source_preserves_all(tmp_dir: Path):
    src = _write(tmp_dir / "src.env", "FOO=old\nBAR=keep\n")
    ref = _write(tmp_dir / "ref.env", "FOO=new\n")
    dedup_keys(src, ref, keep="source")
    result = src.read_text()
    assert "FOO" in result
    assert "BAR" in result


def test_dedup_keys_writes_to_dest(tmp_dir: Path):
    src = _write(tmp_dir / "src.env", "FOO=1\nBAR=2\n")
    ref = _write(tmp_dir / "ref.env", "FOO=10\n")
    dest = tmp_dir / "out.env"
    result = dedup_keys(src, ref, dest=dest, keep="reference")
    assert result == dest.resolve()
    assert dest.exists()
    assert "BAR" in dest.read_text()


def test_dedup_keys_missing_source_raises(tmp_dir: Path):
    ref = _write(tmp_dir / "ref.env", "FOO=1\n")
    with pytest.raises(DedupKeysError, match="Source file not found"):
        dedup_keys(tmp_dir / "nope.env", ref)


def test_dedup_keys_missing_reference_raises(tmp_dir: Path):
    src = _write(tmp_dir / "src.env", "FOO=1\n")
    with pytest.raises(DedupKeysError, match="Reference file not found"):
        dedup_keys(src, tmp_dir / "nope.env")


def test_dedup_keys_invalid_keep_raises(tmp_dir: Path):
    src = _write(tmp_dir / "src.env", "FOO=1\n")
    ref = _write(tmp_dir / "ref.env", "FOO=1\n")
    with pytest.raises(DedupKeysError, match="keep must be"):
        dedup_keys(src, ref, keep="invalid")
