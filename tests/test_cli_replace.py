"""Tests for envault.cli_replace."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from envault.cli_replace import cmd_replace, register_subcommand


def _ns(**kwargs) -> argparse.Namespace:
    defaults = dict(
        pattern="old",
        replacement="new",
        file=None,
        dest=None,
        keys=None,
        literal=False,
        count=0,
        config=".envault.json",
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture()
def mock_config(tmp_path: Path):
    cfg = MagicMock()
    cfg.env_file = str(tmp_path / ".env")
    return cfg


def test_cmd_replace_success(mock_config, tmp_path: Path, capsys) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=old\n")
    mock_config.env_file = str(env_file)

    with patch("envault.cli_replace._load_config", return_value=mock_config), \
         patch("envault.cli_replace.replace_value", return_value=(env_file, 1)) as mock_rv:
        cmd_replace(_ns())

    mock_rv.assert_called_once()
    out = capsys.readouterr().out
    assert "replaced 1" in out


def test_cmd_replace_no_match(mock_config, tmp_path: Path, capsys) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=value\n")
    mock_config.env_file = str(env_file)

    with patch("envault.cli_replace._load_config", return_value=mock_config), \
         patch("envault.cli_replace.replace_value", return_value=(env_file, 0)):
        cmd_replace(_ns())

    assert "no lines matched" in capsys.readouterr().out


def test_cmd_replace_config_error_exits(capsys) -> None:
    from envault.config import ConfigError
    with patch("envault.cli_replace._load_config", side_effect=ConfigError("bad")), \
         pytest.raises(SystemExit) as exc_info:
        cmd_replace(_ns())
    assert exc_info.value.code == 1


def test_cmd_replace_replace_error_exits(mock_config, capsys) -> None:
    from envault.env_replace import ReplaceError
    with patch("envault.cli_replace._load_config", return_value=mock_config), \
         patch("envault.cli_replace.replace_value", side_effect=ReplaceError("oops")), \
         pytest.raises(SystemExit) as exc_info:
        cmd_replace(_ns())
    assert exc_info.value.code == 1


def test_register_subcommand_adds_parser() -> None:
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    register_subcommand(sub)
    ns = root.parse_args(["replace", "old", "new"])
    assert ns.pattern == "old"
    assert ns.replacement == "new"
