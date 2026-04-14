"""Tests for envault/cli_status.py."""
from __future__ import annotations

import argparse
from unittest.mock import MagicMock, patch

import pytest

from envault.cli_status import cmd_status, register_subcommand
from envault.env_status import VaultStatus


def _ns(**kwargs):
    defaults = {"config": ".envault.json", "exit_code": False, "func": cmd_status}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture()
def mock_config():
    cfg = MagicMock()
    cfg.env_file = ".env"
    cfg.encrypted_file = ".env.gpg"
    return cfg


@pytest.fixture()
def healthy_status():
    return VaultStatus(
        env_file=".env",
        env_exists=True,
        encrypted_file=".env.gpg",
        encrypted_exists=True,
        manifest_file=".env.manifest",
        manifest_exists=True,
        manifest_ok=True,
        recipients=["alice@example.com"],
        encrypted_sha256="a" * 64,
    )


def test_cmd_status_success(capsys, mock_config, healthy_status):
    with patch("envault.cli_status.EnvaultConfig.load", return_value=mock_config), \
         patch("envault.cli_status.get_status", return_value=healthy_status):
        cmd_status(_ns())
    out = capsys.readouterr().out
    assert "envault status" in out
    assert "alice@example.com" in out


def test_cmd_status_config_error_exits(capsys):
    from envault.config import ConfigError
    with patch("envault.cli_status.EnvaultConfig.load", side_effect=ConfigError("bad")):
        with pytest.raises(SystemExit) as exc:
            cmd_status(_ns())
    assert exc.value.code == 1


def test_cmd_status_exit_code_when_encrypted_missing(capsys, mock_config):
    bad_status = VaultStatus(
        env_file=".env", env_exists=True,
        encrypted_file=".env.gpg", encrypted_exists=False,
        manifest_file=".env.manifest", manifest_exists=False,
        manifest_ok=None, recipients=[],
    )
    with patch("envault.cli_status.EnvaultConfig.load", return_value=mock_config), \
         patch("envault.cli_status.get_status", return_value=bad_status):
        with pytest.raises(SystemExit) as exc:
            cmd_status(_ns(exit_code=True))
    assert exc.value.code == 2


def test_cmd_status_exit_code_manifest_mismatch(capsys, mock_config):
    bad_status = VaultStatus(
        env_file=".env", env_exists=True,
        encrypted_file=".env.gpg", encrypted_exists=True,
        manifest_file=".env.manifest", manifest_exists=True,
        manifest_ok=False, recipients=[],
    )
    with patch("envault.cli_status.EnvaultConfig.load", return_value=mock_config), \
         patch("envault.cli_status.get_status", return_value=bad_status):
        with pytest.raises(SystemExit) as exc:
            cmd_status(_ns(exit_code=True))
    assert exc.value.code == 3


def test_register_subcommand_adds_status_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_subcommand(sub)
    ns = parser.parse_args(["status"])
    assert ns.func is cmd_status
    assert ns.exit_code is False
