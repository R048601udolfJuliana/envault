"""Tests for envault.cli_scope."""
from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from envault.cli_scope import cmd_scope, register_subcommand


def _ns(**kwargs) -> argparse.Namespace:
    defaults = {
        "scope": "dev",
        "src": None,
        "dest": None,
        "strip_prefix": False,
        "scoped_only": False,
        "config": ".envault.json",
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture()
def mock_config(tmp_path: Path):
    cfg = MagicMock()
    cfg.env_file = str(tmp_path / ".env")
    return cfg


def test_cmd_scope_success(tmp_path: Path, mock_config, capsys) -> None:
    out_path = tmp_path / ".env.dev"
    with patch("envault.cli_scope._load_config", return_value=mock_config), \
         patch("envault.cli_scope.scope_env", return_value=out_path) as mock_scope:
        cmd_scope(_ns())
    mock_scope.assert_called_once()
    captured = capsys.readouterr()
    assert ".env.dev" in captured.out


def test_cmd_scope_error_exits(mock_config) -> None:
    from envault.env_scope import ScopeError
    with patch("envault.cli_scope._load_config", return_value=mock_config), \
         patch("envault.cli_scope.scope_env", side_effect=ScopeError("bad")), \
         pytest.raises(SystemExit) as exc:
        cmd_scope(_ns())
    assert exc.value.code == 1


def test_cmd_scope_config_error_exits() -> None:
    from envault.config import ConfigError
    with patch("envault.cli_scope.EnvaultConfig") as MockCfg, \
         pytest.raises(SystemExit) as exc:
        MockCfg.load.side_effect = ConfigError("missing")
        cmd_scope(_ns())
    assert exc.value.code == 1


def test_register_subcommand_adds_scope_parser() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_subcommand(sub)
    ns = parser.parse_args(["scope", "prod", "--strip-prefix"])
    assert ns.scope == "prod"
    assert ns.strip_prefix is True
