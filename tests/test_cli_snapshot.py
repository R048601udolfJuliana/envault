"""Tests for envault.cli_snapshot."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from envault.cli_snapshot import (
    cmd_snapshot_delete,
    cmd_snapshot_list,
    cmd_snapshot_restore,
    cmd_snapshot_save,
)
from envault.snapshot import SnapshotError


def _ns(**kwargs) -> argparse.Namespace:
    defaults = {"config": None, "snapshot_name": "snap1"}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture()
def mock_config(tmp_path: Path):
    enc = tmp_path / ".env.gpg"
    enc.write_bytes(b"data")
    cfg = MagicMock()
    cfg.encrypted_file = str(enc)
    return cfg


def test_cmd_snapshot_save_success(mock_config, capsys):
    with patch("envault.cli_snapshot._load_config", return_value=mock_config), \
         patch("envault.cli_snapshot.save_snapshot", return_value={"name": "snap1", "timestamp": "2024-01-01T00:00:00+00:00", "file": "snap1.gpg"}) as m_save:
        cmd_snapshot_save(_ns())
    m_save.assert_called_once()
    out = capsys.readouterr().out
    assert "snap1" in out


def test_cmd_snapshot_save_error_exits(mock_config):
    with patch("envault.cli_snapshot._load_config", return_value=mock_config), \
         patch("envault.cli_snapshot.save_snapshot", side_effect=SnapshotError("boom")):
        with pytest.raises(SystemExit) as exc_info:
            cmd_snapshot_save(_ns())
    assert exc_info.value.code == 1


def test_cmd_snapshot_restore_success(mock_config, capsys):
    with patch("envault.cli_snapshot._load_config", return_value=mock_config), \
         patch("envault.cli_snapshot.restore_snapshot") as m_restore:
        cmd_snapshot_restore(_ns())
    m_restore.assert_called_once()
    assert "snap1" in capsys.readouterr().out


def test_cmd_snapshot_list_empty(mock_config, capsys):
    with patch("envault.cli_snapshot._load_config", return_value=mock_config), \
         patch("envault.cli_snapshot.list_snapshots", return_value=[]):
        cmd_snapshot_list(_ns())
    assert "No snapshots" in capsys.readouterr().out


def test_cmd_snapshot_list_with_entries(mock_config, capsys):
    entries = [
        {"name": "v1", "timestamp": "2024-01-01T00:00:00+00:00", "file": "v1.gpg"},
        {"name": "v2", "timestamp": "2024-02-01T00:00:00+00:00", "file": "v2.gpg"},
    ]
    with patch("envault.cli_snapshot._load_config", return_value=mock_config), \
         patch("envault.cli_snapshot.list_snapshots", return_value=entries):
        cmd_snapshot_list(_ns())
    out = capsys.readouterr().out
    assert "v1" in out and "v2" in out


def test_cmd_snapshot_delete_success(mock_config, capsys):
    with patch("envault.cli_snapshot._load_config", return_value=mock_config), \
         patch("envault.cli_snapshot.delete_snapshot") as m_del:
        cmd_snapshot_delete(_ns())
    m_del.assert_called_once()
    assert "snap1" in capsys.readouterr().out


def test_cmd_snapshot_delete_error_exits(mock_config):
    with patch("envault.cli_snapshot._load_config", return_value=mock_config), \
         patch("envault.cli_snapshot.delete_snapshot", side_effect=SnapshotError("not found")):
        with pytest.raises(SystemExit) as exc_info:
            cmd_snapshot_delete(_ns())
    assert exc_info.value.code == 1
