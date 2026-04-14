"""Tests for envault.backup."""
from __future__ import annotations

import time
from pathlib import Path

import pytest

from envault.backup import (
    BackupError,
    create_backup,
    delete_backup,
    list_backups,
    restore_backup,
)


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture()
def enc_file(tmp_dir: Path) -> Path:
    f = tmp_dir / "secrets.env.gpg"
    f.write_bytes(b"encrypted-content")
    return f


def test_create_backup_returns_path(enc_file: Path, tmp_dir: Path) -> None:
    bak = create_backup(enc_file, backup_root=tmp_dir)
    assert bak.exists()
    assert bak.suffix == ".bak"


def test_create_backup_content_matches(enc_file: Path, tmp_dir: Path) -> None:
    bak = create_backup(enc_file, backup_root=tmp_dir)
    assert bak.read_bytes() == b"encrypted-content"


def test_create_backup_missing_file_raises(tmp_dir: Path) -> None:
    missing = tmp_dir / "ghost.env.gpg"
    with pytest.raises(BackupError, match="not found"):
        create_backup(missing, backup_root=tmp_dir)


def test_list_backups_empty_when_none_exist(enc_file: Path, tmp_dir: Path) -> None:
    result = list_backups(enc_file, backup_root=tmp_dir)
    assert result == []


def test_list_backups_returns_created_backup(enc_file: Path, tmp_dir: Path) -> None:
    bak = create_backup(enc_file, backup_root=tmp_dir)
    result = list_backups(enc_file, backup_root=tmp_dir)
    assert bak in result


def test_list_backups_sorted_oldest_first(enc_file: Path, tmp_dir: Path) -> None:
    bak1 = create_backup(enc_file, backup_root=tmp_dir)
    time.sleep(1.1)  # ensure different timestamp
    bak2 = create_backup(enc_file, backup_root=tmp_dir)
    result = list_backups(enc_file, backup_root=tmp_dir)
    assert result.index(bak1) < result.index(bak2)


def test_restore_backup_overwrites_encrypted_file(enc_file: Path, tmp_dir: Path) -> None:
    bak = create_backup(enc_file, backup_root=tmp_dir)
    enc_file.write_bytes(b"new-content")
    restore_backup(bak, enc_file)
    assert enc_file.read_bytes() == b"encrypted-content"


def test_restore_backup_missing_raises(tmp_dir: Path, enc_file: Path) -> None:
    ghost = tmp_dir / "ghost.bak"
    with pytest.raises(BackupError, match="not found"):
        restore_backup(ghost, enc_file)


def test_delete_backup_removes_file(enc_file: Path, tmp_dir: Path) -> None:
    bak = create_backup(enc_file, backup_root=tmp_dir)
    delete_backup(bak)
    assert not bak.exists()


def test_delete_backup_missing_raises(tmp_dir: Path) -> None:
    ghost = tmp_dir / "ghost.bak"
    with pytest.raises(BackupError, match="not found"):
        delete_backup(ghost)
