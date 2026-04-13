"""Tests for envault.history and envault.cli_history."""

from __future__ import annotations

import json
import time
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from envault.history import (
    HistoryEntry,
    HistoryError,
    _MAX_ENTRIES,
    clear_history,
    load_history,
    record,
)
from envault.cli_history import cmd_history_clear, cmd_history_list


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_load_history_missing_file_returns_empty(tmp_dir):
    assert load_history(tmp_dir) == []


def test_record_creates_entry(tmp_dir):
    entry = record(tmp_dir, "push", "env.gpg", recipients=["alice@example.com"])
    assert entry.action == "push"
    assert entry.encrypted_file == "env.gpg"
    assert "alice@example.com" in entry.recipients
    assert isinstance(entry.timestamp, float)


def test_record_persists_to_disk(tmp_dir):
    record(tmp_dir, "pull", "env.gpg", note="initial pull")
    entries = load_history(tmp_dir)
    assert len(entries) == 1
    assert entries[0].action == "pull"
    assert entries[0].note == "initial pull"


def test_record_multiple_entries(tmp_dir):
    record(tmp_dir, "push", "env.gpg")
    record(tmp_dir, "pull", "env.gpg")
    entries = load_history(tmp_dir)
    assert len(entries) == 2


def test_history_capped_at_max_entries(tmp_dir):
    for i in range(_MAX_ENTRIES + 5):
        record(tmp_dir, "push", f"env{i}.gpg")
    entries = load_history(tmp_dir)
    assert len(entries) == _MAX_ENTRIES


def test_load_history_invalid_json_raises(tmp_dir):
    (tmp_dir / ".envault_history.json").write_text("not-json", encoding="utf-8")
    with pytest.raises(HistoryError):
        load_history(tmp_dir)


def test_clear_history_removes_file(tmp_dir):
    record(tmp_dir, "push", "env.gpg")
    clear_history(tmp_dir)
    assert not (tmp_dir / ".envault_history.json").exists()


def test_clear_history_noop_when_missing(tmp_dir):
    clear_history(tmp_dir)  # should not raise


def test_history_entry_human_time():
    ts = time.mktime(time.strptime("2024-06-01 12:00:00", "%Y-%m-%d %H:%M:%S"))
    entry = HistoryEntry(action="push", timestamp=ts, encrypted_file="env.gpg")
    assert "2024-06-01" in entry.human_time()


def _ns(**kwargs):
    return SimpleNamespace(**kwargs)


def test_cmd_history_list_empty(tmp_dir, capsys):
    args = _ns(dir=str(tmp_dir), limit=None)
    cmd_history_list(args)
    out = capsys.readouterr().out
    assert "No history" in out


def test_cmd_history_list_shows_entries(tmp_dir, capsys):
    record(tmp_dir, "push", "env.gpg", recipients=["bob@example.com"])
    args = _ns(dir=str(tmp_dir), limit=None)
    cmd_history_list(args)
    out = capsys.readouterr().out
    assert "push" in out
    assert "bob@example.com" in out


def test_cmd_history_clear_success(tmp_dir, capsys):
    record(tmp_dir, "push", "env.gpg")
    args = _ns(dir=str(tmp_dir))
    cmd_history_clear(args)
    out = capsys.readouterr().out
    assert "cleared" in out
    assert load_history(tmp_dir) == []
