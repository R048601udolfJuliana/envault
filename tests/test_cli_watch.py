"""Tests for envault.cli_watch."""

import argparse
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from envault.cli_watch import cmd_watch, register_subcommand
from envault.watch import WatchError
from envault.sync import SyncError


def _ns(**kwargs) -> argparse.Namespace:
    defaults = {"config": ".envault.json", "interval": 1.0}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture()
def mock_config(tmp_path: Path):
    cfg = MagicMock()
    cfg.env_file = str(tmp_path / ".env")
    (tmp_path / ".env").write_text("A=1\n")
    return cfg


def test_register_subcommand_adds_watch_parser() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_subcommand(sub)
    ns = parser.parse_args(["watch", "--interval", "2.5"])
    assert ns.interval == 2.5


def test_cmd_watch_exits_on_config_error() -> None:
    with patch("envault.cli_watch._load_config", side_effect=SystemExit(1)):
        with pytest.raises(SystemExit) as exc_info:
            cmd_watch(_ns())
    assert exc_info.value.code == 1


def test_cmd_watch_exits_on_watch_error(mock_config) -> None:
    with patch("envault.cli_watch._load_config", return_value=mock_config), \
         patch("envault.cli_watch.watch", side_effect=WatchError("gone")):
        with pytest.raises(SystemExit) as exc_info:
            cmd_watch(_ns())
    assert exc_info.value.code == 1


def test_cmd_watch_stops_on_keyboard_interrupt(mock_config, capsys) -> None:
    with patch("envault.cli_watch._load_config", return_value=mock_config), \
         patch("envault.cli_watch.watch", side_effect=KeyboardInterrupt):
        cmd_watch(_ns())  # should NOT raise
    out = capsys.readouterr().out
    assert "Stopped watching" in out


def test_cmd_watch_on_change_calls_push(mock_config) -> None:
    captured_callback = {}

    def fake_watch(path, on_change, interval, max_iterations=None):
        captured_callback["fn"] = on_change

    with patch("envault.cli_watch._load_config", return_value=mock_config), \
         patch("envault.cli_watch.watch", side_effect=fake_watch), \
         patch("envault.cli_watch.push") as mock_push:
        cmd_watch(_ns())
        captured_callback["fn"](Path(mock_config.env_file))
        mock_push.assert_called_once_with(mock_config, force=True)


def test_cmd_watch_on_change_handles_sync_error(mock_config, capsys) -> None:
    captured_callback = {}

    def fake_watch(path, on_change, interval, max_iterations=None):
        captured_callback["fn"] = on_change

    with patch("envault.cli_watch._load_config", return_value=mock_config), \
         patch("envault.cli_watch.watch", side_effect=fake_watch), \
         patch("envault.cli_watch.push", side_effect=SyncError("fail")):
        cmd_watch(_ns())
        captured_callback["fn"](Path(mock_config.env_file))  # should not raise
    err = capsys.readouterr().err
    assert "Push failed" in err
