"""Tests for envault.remind."""
from __future__ import annotations

import json
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from envault.remind import (
    RemindError,
    check_rotation_due,
    days_since_rotation,
    load_last_rotation,
    record_rotation,
)


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_record_rotation_creates_file(tmp_dir: Path) -> None:
    record_rotation(tmp_dir)
    remind_file = tmp_dir / ".envault_remind.json"
    assert remind_file.exists()


def test_record_rotation_stores_timestamp(tmp_dir: Path) -> None:
    before = time.time()
    record_rotation(tmp_dir)
    after = time.time()
    ts = load_last_rotation(tmp_dir)
    assert ts is not None
    assert before <= ts <= after


def test_load_last_rotation_missing_returns_none(tmp_dir: Path) -> None:
    assert load_last_rotation(tmp_dir) is None


def test_load_last_rotation_corrupt_raises(tmp_dir: Path) -> None:
    (tmp_dir / ".envault_remind.json").write_text("{invalid json")
    with pytest.raises(RemindError):
        load_last_rotation(tmp_dir)


def test_load_last_rotation_missing_key_raises(tmp_dir: Path) -> None:
    (tmp_dir / ".envault_remind.json").write_text(json.dumps({"other": 1}))
    with pytest.raises(RemindError):
        load_last_rotation(tmp_dir)


def test_check_rotation_due_when_never_recorded(tmp_dir: Path) -> None:
    assert check_rotation_due(tmp_dir, max_age_days=30) is True


def test_check_rotation_due_when_recent(tmp_dir: Path) -> None:
    record_rotation(tmp_dir)
    assert check_rotation_due(tmp_dir, max_age_days=30) is False


def test_check_rotation_due_when_old(tmp_dir: Path) -> None:
    old_ts = time.time() - (31 * 86400)
    (tmp_dir / ".envault_remind.json").write_text(json.dumps({"last_rotated": old_ts}))
    assert check_rotation_due(tmp_dir, max_age_days=30) is True


def test_days_since_rotation_none_when_missing(tmp_dir: Path) -> None:
    assert days_since_rotation(tmp_dir) is None


def test_days_since_rotation_approximate(tmp_dir: Path) -> None:
    ts = time.time() - 5 * 86400
    (tmp_dir / ".envault_remind.json").write_text(json.dumps({"last_rotated": ts}))
    days = days_since_rotation(tmp_dir)
    assert days is not None
    assert 4.9 < days < 5.1
