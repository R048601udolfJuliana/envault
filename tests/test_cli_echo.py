"""Tests for envault/cli_echo.py."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from envault.cli_echo import cmd_echo, register_subcommand


def _ns(**kwargs) -> argparse.Namespace:
    defaults = {
        "config": ".envault.json",
        "file": None,
        "fmt": "plain",
        "keys": None,
        "mask": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture()
def mock_config(tmp_path: Path):
    cfg = MagicMock()
    cfg.env_file = str(tmp_path / ".env")
    return cfg


def test_cmd_echo_success(tmp_path: Path, mock_config, capsys) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("FOO=bar\n", encoding="utf-8")
    mock_config.env_file = str(env_file)

    with patch("envault.cli_echo._load_config", return_value=mock_config):
        cmd_echo(_ns())

    captured = capsys.readouterr()
    assert "FOO=bar" in captured.out


def test_cmd_echo_config_error_exits(capsys) -> None:
    from envault.config import ConfigError

    with patch("envault.cli_echo._load_config", side_effect=ConfigError("bad config")):
        with pytest.raises(SystemExit) as exc_info:
            cmd_echo(_ns())
    assert exc_info.value.code == 1
    assert "config" in capsys.readouterr().err


def test_cmd_echo_echo_error_exits(tmp_path: Path, mock_config, capsys) -> None:
    from envault.env_echo import EchoError

    with patch("envault.cli_echo._load_config", return_value=mock_config), patch(
        "envault.cli_echo.echo_env", side_effect=EchoError("missing")
    ):
        with pytest.raises(SystemExit) as exc_info:
            cmd_echo(_ns())
    assert exc_info.value.code == 1
    assert "missing" in capsys.readouterr().err


def test_cmd_echo_export_format(tmp_path: Path, mock_config, capsys) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("A=1\n", encoding="utf-8")
    mock_config.env_file = str(env_file)

    with patch("envault.cli_echo._load_config", return_value=mock_config):
        cmd_echo(_ns(fmt="export"))

    assert "export A=1" in capsys.readouterr().out


def test_register_subcommand_adds_echo_parser() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_subcommand(sub)
    args = parser.parse_args(["echo", "--fmt", "json"])
    assert args.fmt == "json"
