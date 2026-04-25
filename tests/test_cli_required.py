"""Tests for envault.cli_required."""
from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from envault.cli_required import cmd_required, register_subcommand
from envault.env_required import MissingKey, RequiredError, RequiredResult


def _ns(**kwargs) -> argparse.Namespace:
    defaults = {
        "config": ".envault.json",
        "env_file": None,
        "keys": ["FOO"],
        "allow_empty": False,
        "strict": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture()
def mock_config(tmp_path: Path):
    cfg = MagicMock()
    cfg.env_file = str(tmp_path / ".env")
    return cfg


def test_cmd_required_success(mock_config, capsys):
    ok_result = RequiredResult()
    with patch("envault.cli_required._load_config", return_value=mock_config), \
         patch("envault.cli_required.check_required", return_value=ok_result):
        cmd_required(_ns(keys=["FOO"]))
    out = capsys.readouterr().out
    assert "present" in out


def test_cmd_required_missing_exits(mock_config):
    bad = RequiredResult(missing=[MissingKey("FOO", "absent")])
    with patch("envault.cli_required._load_config", return_value=mock_config), \
         patch("envault.cli_required.check_required", return_value=bad):
        # strict=False — should NOT raise SystemExit
        cmd_required(_ns(keys=["FOO"], strict=False))


def test_cmd_required_strict_exits(mock_config):
    bad = RequiredResult(missing=[MissingKey("FOO", "absent")])
    with patch("envault.cli_required._load_config", return_value=mock_config), \
         patch("envault.cli_required.check_required", return_value=bad), \
         pytest.raises(SystemExit) as exc_info:
        cmd_required(_ns(keys=["FOO"], strict=True))
    assert exc_info.value.code == 1


def test_cmd_required_error_exits(mock_config):
    with patch("envault.cli_required._load_config", return_value=mock_config), \
         patch("envault.cli_required.check_required", side_effect=RequiredError("oops")), \
         pytest.raises(SystemExit) as exc_info:
        cmd_required(_ns(keys=["FOO"]))
    assert exc_info.value.code == 1


def test_cmd_required_config_error_exits():
    from envault.config import ConfigError
    with patch("envault.cli_required._load_config", side_effect=ConfigError("bad")), \
         pytest.raises(SystemExit) as exc_info:
        cmd_required(_ns())
    assert exc_info.value.code == 1


def test_cmd_required_no_keys_exits(mock_config):
    with patch("envault.cli_required._load_config", return_value=mock_config), \
         pytest.raises(SystemExit) as exc_info:
        cmd_required(_ns(keys=[]))
    assert exc_info.value.code == 1


def test_register_subcommand_adds_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_subcommand(sub)
    args = parser.parse_args(["required", "FOO", "BAR"])
    assert args.keys == ["FOO", "BAR"]
    assert args.strict is False
    assert args.allow_empty is False
