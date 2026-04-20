"""Tests for envault.cli_trim."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from envault.cli_trim import cmd_trim, register_subcommand
from envault.env_trim import TrimError


def _ns(**kwargs) -> argparse.Namespace:
    defaults = {
        "file": None,
        "dest": None,
        "dry_run": False,
        "config": ".envault.json",
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture()
def mock_config(tmp_path: Path):
    cfg = MagicMock()
    cfg.env_file = str(tmp_path / ".env")
    return cfg


def test_cmd_trim_success(mock_config, capsys):
    with patch("envault.cli_trim._load_config", return_value=mock_config), \
         patch("envault.cli_trim.trim_env", return_value=3) as m_trim:
        cmd_trim(_ns())
    m_trim.assert_called_once()
    out = capsys.readouterr().out
    assert "3" in out


def test_cmd_trim_dry_run_message(mock_config, capsys):
    with patch("envault.cli_trim._load_config", return_value=mock_config), \
         patch("envault.cli_trim.trim_env", return_value=2):
        cmd_trim(_ns(dry_run=True))
    out = capsys.readouterr().out
    assert "dry-run" in out
    assert "2" in out


def test_cmd_trim_nothing_to_trim(mock_config, capsys):
    with patch("envault.cli_trim._load_config", return_value=mock_config), \
         patch("envault.cli_trim.trim_env", return_value=0):
        cmd_trim(_ns())
    out = capsys.readouterr().out
    assert "nothing" in out


def test_cmd_trim_error_exits(mock_config):
    with patch("envault.cli_trim._load_config", return_value=mock_config), \
         patch("envault.cli_trim.trim_env", side_effect=TrimError("bad")):
        with pytest.raises(SystemExit) as exc_info:
            cmd_trim(_ns())
    assert exc_info.value.code == 1


def test_register_subcommand_adds_trim_parser():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers()
    register_subcommand(subs)
    ns = parser.parse_args(["trim", "--dry-run"])
    assert ns.dry_run is True
