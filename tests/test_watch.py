"""Tests for envault.watch."""

import time
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from envault.watch import watch, WatchError, _mtime


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text("KEY=value\n")
    return f


def test_mtime_returns_float_for_existing_file(env_file: Path) -> None:
    result = _mtime(env_file)
    assert isinstance(result, float)
    assert result > 0.0


def test_mtime_returns_zero_for_missing_file(tmp_path: Path) -> None:
    assert _mtime(tmp_path / "nonexistent.env") == 0.0


def test_watch_raises_when_file_missing(tmp_path: Path) -> None:
    with pytest.raises(WatchError, match="File not found"):
        watch(tmp_path / "missing.env", on_change=MagicMock(), interval=0.01, max_iterations=1)


def test_watch_no_callback_when_unchanged(env_file: Path) -> None:
    callback = MagicMock()
    watch(env_file, on_change=callback, interval=0.01, max_iterations=3)
    callback.assert_not_called()


def test_watch_calls_callback_on_change(env_file: Path, tmp_path: Path) -> None:
    callback = MagicMock()
    called_after = [False]

    original_sleep = time.sleep

    iteration = [0]

    def fake_sleep(secs: float) -> None:  # noqa: ARG001
        iteration[0] += 1
        if iteration[0] == 1:
            env_file.write_text("KEY=changed\n")
        original_sleep(0.001)

    import unittest.mock as mock

    with mock.patch("envault.watch.time.sleep", side_effect=fake_sleep):
        watch(env_file, on_change=callback, interval=0.01, max_iterations=2)

    callback.assert_called_once_with(env_file)


def test_watch_stops_after_max_iterations(env_file: Path) -> None:
    callback = MagicMock()
    # Should return without raising after exactly 5 iterations
    watch(env_file, on_change=callback, interval=0.001, max_iterations=5)
    # No assertion on callback — just verifying it doesn't loop forever
