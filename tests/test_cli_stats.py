"""Tests for envault.cli_stats"""
import argparse
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from envault.cli_stats import cmd_stats, register_subcommand
from envault.env_stats import EnvStats


def _ns(**kwargs):
    defaults = {"config": ".envault.json", "file": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture
def mock_config(tmp_path):
    cfg = MagicMock()
    cfg.env_file = str(tmp_path / ".env")
    return cfg


def test_cmd_stats_success(mock_config, capsys):
    stats = EnvStats(total_keys=3, empty_values=1, comment_lines=2, blank_lines=1,
                     longest_key="MYKEY", longest_value_key="OTHER")
    with patch("envault.cli_stats._load_config", return_value=mock_config), \
         patch("envault.cli_stats.compute_stats", return_value=stats):
        cmd_stats(_ns())
    out = capsys.readouterr().out
    assert "Total keys" in out
    assert "3" in out


def test_cmd_stats_config_error_exits():
    from envault.config import ConfigError
    with patch("envault.cli_stats._load_config", side_effect=ConfigError("bad")):
        with pytest.raises(SystemExit) as exc:
            cmd_stats(_ns())
    assert exc.value.code == 1


def test_cmd_stats_stats_error_exits(mock_config):
    from envault.env_stats import StatsError
    with patch("envault.cli_stats._load_config", return_value=mock_config), \
         patch("envault.cli_stats.compute_stats", side_effect=StatsError("missing")):
        with pytest.raises(SystemExit) as exc:
            cmd_stats(_ns())
    assert exc.value.code == 1


def test_register_subcommand_adds_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_subcommand(sub)
    args = parser.parse_args(["stats"])
    assert hasattr(args, "func")
