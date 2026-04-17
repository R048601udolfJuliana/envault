"""Tests for envault.schedule."""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from envault.schedule import (
    ScheduleError,
    check_schedule_due,
    delete_schedule,
    load_schedule,
    save_schedule,
)


@pytest.fixture
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_save_and_load_roundtrip(tmp_dir):
    save_schedule(tmp_dir, 7)
    s = load_schedule(tmp_dir)
    assert s is not None
    assert s["interval_days"] == 7


def test_save_invalid_interval_raises(tmp_dir):
    with pytest.raises(ScheduleError):
        save_schedule(tmp_dir, 0)


def test_load_missing_returns_none(tmp_dir):
    assert load_schedule(tmp_dir) is None


def test_load_corrupt_raises(tmp_dir):
    (tmp_dir / ".envault_schedule.json").write_text("not json")
    with pytest.raises(ScheduleError):
        load_schedule(tmp_dir)


def test_delete_schedule(tmp_dir):
    save_schedule(tmp_dir, 3)
    delete_schedule(tmp_dir)
    assert load_schedule(tmp_dir) is None


def test_delete_missing_raises(tmp_dir):
    with pytest.raises(ScheduleError):
        delete_schedule(tmp_dir)


def test_check_due_no_schedule(tmp_dir):
    assert check_schedule_due(tmp_dir, None) is False


def test_check_due_no_last_push(tmp_dir):
    save_schedule(tmp_dir, 7)
    assert check_schedule_due(tmp_dir, None) is True


def test_check_not_yet_due(tmp_dir):
    save_schedule(tmp_dir, 7)
    recent = (datetime.utcnow() - timedelta(days=2)).isoformat()
    assert check_schedule_due(tmp_dir, recent) is False


def test_check_overdue(tmp_dir):
    save_schedule(tmp_dir, 7)
    old = (datetime.utcnow() - timedelta(days=10)).isoformat()
    assert check_schedule_due(tmp_dir, old) is True
