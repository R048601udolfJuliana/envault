"""Tests for envault.ttl."""
from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from envault.ttl import (
    TTLError,
    clear_ttl,
    is_expired,
    load_ttl,
    remaining_seconds,
    set_ttl,
)


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_set_ttl_creates_file(tmp_dir):
    set_ttl(tmp_dir, 3600)
    assert (tmp_dir / ".envault_ttl").exists()


def test_set_ttl_stores_correct_seconds(tmp_dir):
    set_ttl(tmp_dir, 600)
    data = json.loads((tmp_dir / ".envault_ttl").read_text())
    assert data["ttl_seconds"] == 600


def test_set_ttl_zero_raises(tmp_dir):
    with pytest.raises(TTLError):
        set_ttl(tmp_dir, 0)


def test_set_ttl_negative_raises(tmp_dir):
    with pytest.raises(TTLError):
        set_ttl(tmp_dir, -10)


def test_load_ttl_returns_none_when_missing(tmp_dir):
    assert load_ttl(tmp_dir) is None


def test_load_ttl_returns_dict(tmp_dir):
    set_ttl(tmp_dir, 100)
    data = load_ttl(tmp_dir)
    assert isinstance(data, dict)
    assert "created_at" in data


def test_load_ttl_corrupt_raises(tmp_dir):
    (tmp_dir / ".envault_ttl").write_text("not json")
    with pytest.raises(TTLError):
        load_ttl(tmp_dir)


def test_is_expired_false_for_future_ttl(tmp_dir):
    set_ttl(tmp_dir, 9999)
    assert is_expired(tmp_dir) is False


def test_is_expired_true_for_past_ttl(tmp_dir):
    data = {"created_at": time.time() - 100, "ttl_seconds": 10}
    (tmp_dir / ".envault_ttl").write_text(json.dumps(data))
    assert is_expired(tmp_dir) is True


def test_is_expired_false_when_no_ttl(tmp_dir):
    assert is_expired(tmp_dir) is False


def test_remaining_seconds_none_when_not_set(tmp_dir):
    assert remaining_seconds(tmp_dir) is None


def test_remaining_seconds_positive_for_future(tmp_dir):
    set_ttl(tmp_dir, 3600)
    rem = remaining_seconds(tmp_dir)
    assert rem is not None
    assert rem > 3590


def test_remaining_seconds_zero_when_expired(tmp_dir):
    data = {"created_at": time.time() - 200, "ttl_seconds": 10}
    (tmp_dir / ".envault_ttl").write_text(json.dumps(data))
    assert remaining_seconds(tmp_dir) == 0.0


def test_clear_ttl_removes_file(tmp_dir):
    set_ttl(tmp_dir, 60)
    clear_ttl(tmp_dir)
    assert not (tmp_dir / ".envault_ttl").exists()


def test_clear_ttl_noop_when_missing(tmp_dir):
    clear_ttl(tmp_dir)  # should not raise
