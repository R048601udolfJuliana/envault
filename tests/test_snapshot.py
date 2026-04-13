"""Tests for envault.snapshot."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.snapshot import (
    SnapshotError,
    delete_snapshot,
    list_snapshots,
    restore_snapshot,
    save_snapshot,
    _snapshot_dir,
)


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture()
def enc_file(tmp_dir: Path) -> Path:
    f = tmp_dir / ".env.gpg"
    f.write_bytes(b"ENCRYPTED_CONTENT")
    return f


def test_save_snapshot_creates_file_and_meta(enc_file: Path, tmp_dir: Path) -> None:
    entry = save_snapshot(enc_file, "v1", base=tmp_dir)
    assert entry["name"] == "v1"
    snap_dir = _snapshot_dir(tmp_dir)
    assert (snap_dir / entry["file"]).exists()


def test_save_snapshot_stores_meta(enc_file: Path, tmp_dir: Path) -> None:
    save_snapshot(enc_file, "release-1", base=tmp_dir)
    entries = list_snapshots(tmp_dir)
    assert len(entries) == 1
    assert entries[0]["name"] == "release-1"


def test_save_snapshot_duplicate_name_raises(enc_file: Path, tmp_dir: Path) -> None:
    save_snapshot(enc_file, "dup", base=tmp_dir)
    with pytest.raises(SnapshotError, match="already exists"):
        save_snapshot(enc_file, "dup", base=tmp_dir)


def test_save_snapshot_missing_encrypted_file_raises(tmp_dir: Path) -> None:
    missing = tmp_dir / "ghost.gpg"
    with pytest.raises(SnapshotError, match="not found"):
        save_snapshot(missing, "snap", base=tmp_dir)


def test_restore_snapshot_copies_file(enc_file: Path, tmp_dir: Path) -> None:
    save_snapshot(enc_file, "backup", base=tmp_dir)
    target = tmp_dir / "restored.gpg"
    restore_snapshot("backup", target, base=tmp_dir)
    assert target.read_bytes() == b"ENCRYPTED_CONTENT"


def test_restore_snapshot_unknown_name_raises(tmp_dir: Path) -> None:
    with pytest.raises(SnapshotError, match="not found"):
        restore_snapshot("nonexistent", tmp_dir / "out.gpg", base=tmp_dir)


def test_list_snapshots_empty(tmp_dir: Path) -> None:
    assert list_snapshots(tmp_dir) == []


def test_list_snapshots_multiple(enc_file: Path, tmp_dir: Path) -> None:
    save_snapshot(enc_file, "a", base=tmp_dir)
    save_snapshot(enc_file, "b", base=tmp_dir)
    entries = list_snapshots(tmp_dir)
    names = [e["name"] for e in entries]
    assert names == ["a", "b"]


def test_delete_snapshot_removes_entry_and_file(enc_file: Path, tmp_dir: Path) -> None:
    entry = save_snapshot(enc_file, "to-delete", base=tmp_dir)
    snap_file = _snapshot_dir(tmp_dir) / entry["file"]
    assert snap_file.exists()
    delete_snapshot("to-delete", base=tmp_dir)
    assert not snap_file.exists()
    assert list_snapshots(tmp_dir) == []


def test_delete_snapshot_unknown_raises(tmp_dir: Path) -> None:
    with pytest.raises(SnapshotError, match="not found"):
        delete_snapshot("ghost", base=tmp_dir)
