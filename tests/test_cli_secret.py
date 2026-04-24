"""Tests for envault.cli_secret."""
from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from envault.cli_secret import cmd_secret_scan, register_subcommand
from envault.env_secret import SecretError, SecretMatch, SecretResult


def _ns(**kwargs) -> argparse.Namespace:
    defaults = {
        "config": ".envault.json",
        "file": None,
        "no_entropy": False,
        "no_names": False,
        "strict": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture()
def mock_config(tmp_path: Path):
    cfg = MagicMock()
    cfg.env_file = str(tmp_path / ".env")
    return cfg


def test_register_subcommand_adds_secret_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_subcommand(sub)
    args = parser.parse_args(["secret"])
    assert hasattr(args, "func")


def test_cmd_secret_scan_no_secrets(mock_config, capsys):
    result = SecretResult(matches=[])
    with patch("envault.cli_secret._load_config", return_value=mock_config), \
         patch("envault.cli_secret.scan_secrets", return_value=result):
        cmd_secret_scan(_ns())
    out = capsys.readouterr().out
    assert "No secrets" in out


def test_cmd_secret_scan_with_secrets(mock_config, capsys):
    match = SecretMatch("API_KEY", "abc123", "sensitive key name")
    result = SecretResult(matches=[match])
    with patch("envault.cli_secret._load_config", return_value=mock_config), \
         patch("envault.cli_secret.scan_secrets", return_value=result):
        cmd_secret_scan(_ns())
    out = capsys.readouterr().out
    assert "Detected" in out


def test_cmd_secret_scan_strict_exits_on_findings(mock_config):
    match = SecretMatch("TOKEN", "xyz", "sensitive key name")
    result = SecretResult(matches=[match])
    with patch("envault.cli_secret._load_config", return_value=mock_config), \
         patch("envault.cli_secret.scan_secrets", return_value=result), \
         pytest.raises(SystemExit) as exc_info:
        cmd_secret_scan(_ns(strict=True))
    assert exc_info.value.code == 1


def test_cmd_secret_scan_config_error_exits():
    from envault.config import ConfigError
    with patch("envault.cli_secret._load_config", side_effect=ConfigError("bad")), \
         pytest.raises(SystemExit) as exc_info:
        cmd_secret_scan(_ns())
    assert exc_info.value.code == 1


def test_cmd_secret_scan_secret_error_exits(mock_config):
    with patch("envault.cli_secret._load_config", return_value=mock_config), \
         patch("envault.cli_secret.scan_secrets", side_effect=SecretError("oops")), \
         pytest.raises(SystemExit) as exc_info:
        cmd_secret_scan(_ns())
    assert exc_info.value.code == 1
