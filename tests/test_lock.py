"""Tests for envault.lock."""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from envault.lock import LockError, acquire, is_locked, release


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_acquire_creates_lock_file(tmp_dir):
    lock = acquire(tmp_dir)
    assert lock.exists()
    release(lock)


def test_lock_file_contains_pid(tmp_dir):
    lock = acquire(tmp_dir)
    content = lock.read_text().strip()
    assert content == str(os.getpid())
    release(lock)


def test_release_removes_lock_file(tmp_dir):
    lock = acquire(tmp_dir)
    release(lock)
    assert not lock.exists()


def test_is_locked_false_when_no_lock(tmp_dir):
    assert not is_locked(tmp_dir)


def test_is_locked_true_while_held(tmp_dir):
    lock = acquire(tmp_dir)
    assert is_locked(tmp_dir)
    release(lock)
    assert not is_locked(tmp_dir)


def test_acquire_raises_when_already_locked(tmp_dir):
    lock = acquire(tmp_dir)
    try:
        with pytest.raises(LockError, match="Could not acquire lock"):
            acquire(tmp_dir, timeout=0.3, poll=0.1)
    finally:
        release(lock)


def test_release_raises_when_lock_missing(tmp_dir):
    lock = acquire(tmp_dir)
    release(lock)  # first release is fine
    with pytest.raises(LockError, match="not found"):
        release(lock)


def test_acquire_succeeds_after_release(tmp_dir):
    lock = acquire(tmp_dir)
    release(lock)
    lock2 = acquire(tmp_dir)
    assert lock2.exists()
    release(lock2)
