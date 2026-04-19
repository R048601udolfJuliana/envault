"""Tests for envault.cli_filter."""
from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from envault.cli_filter import cmd_filter, register_subcommand
from envault.env_filter import FilterError


def _ns(**kwargs) -> argparse.Namespace:
    defaults = {
        "config": ".envault.json",
        "dest": "filtered.env",
        "src": "",
        "prefix": "",
        "pattern": "",
        "keys": None,
        "exclude": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture()
def mock_config(tmp_path: Path):
    cfg = MagicMock()
    cfg.env_file = tmp_path / ".env"
    return cfg


def test_cmd_filter_success(tmp_path: Path, mock_config) -> None:
    with patch("envault.cli_filter._load_config", return_value=mock_config), \
         patch("envault.cli_filter.filter_env", return_value=3) as mock_fe:
        ns = _ns(dest=str(tmp_path / "out.env"), prefix="DB_")
        cmd_filter(ns)
        mock_fe.assert_called_once()


def test_cmd_filter_error_exits(tmp_path: Path, mock_config) -> None:
    with patch("envault.cli_filter._load_config", return_value=mock_config), \
         patch("envault.cli_filter.filter_env", side_effect=FilterError("oops")):
        ns = _ns(dest=str(tmp_path / "out.env"), prefix="DB_")
        with pytest.raises(SystemExit) as exc:
            cmd_filter(ns)
        assert exc.value.code == 1


def test_cmd_filter_config_error_exits(tmp_path: Path) -> None:
    from envault.config import ConfigError
    with patch("envault.cli_filter._load_config", side_effect=ConfigError("bad")):
        ns = _ns(dest=str(tmp_path / "out.env"), prefix="DB_")
        with pytest.raises(SystemExit) as exc:
            cmd_filter(ns)
        assert exc.value.code == 1


def test_register_subcommand_adds_parser() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_subcommand(sub)
    args = parser.parse_args(["filter", "out.env", "--prefix", "APP_"])
    assert args.dest == "out.env"
    assert args.prefix == "APP_"
