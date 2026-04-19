"""Tests for envault.cli_rotate."""

from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from envault.cli_rotate import cmd_rotate, register_subcommand
from envault.rotate import RotationError
from envault.config import EnvaultConfig


def _ns(**kwargs) -> argparse.Namespace:
    defaults = {
        "config": None,
        "recipient": [],
        "dry_run": False,
        "audit_file": None,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture()
def mock_config(tmp_path: Path) -> EnvaultConfig:
    return EnvaultConfig(
        recipients=["AABBCCDD"],
        env_file=str(tmp_path / ".env"),
        encrypted_file=str(tmp_path / ".env.gpg"),
    )


def test_cmd_rotate_success(mock_config: EnvaultConfig, capsys):
    with (
        patch("envault.cli_rotate._load_config", return_value=mock_config),
        patch("envault.cli_rotate.passphrase_from_env", return_value=None),
        patch("envault.cli_rotate.rotate", return_value=Path(".env.gpg")) as mock_rotate,
    ):
        cmd_rotate(_ns(recipient=["NEWKEY01"]))

    mock_rotate.assert_called_once()
    out = capsys.readouterr().out
    assert "rotated" in out


def test_cmd_rotate_dry_run(mock_config: EnvaultConfig, capsys):
    with (
        patch("envault.cli_rotate._load_config", return_value=mock_config),
        patch("envault.cli_rotate.passphrase_from_env", return_value=None),
        patch("envault.cli_rotate.rotate", return_value=Path(".env.gpg")),
    ):
        cmd_rotate(_ns(dry_run=True))

    out = capsys.readouterr().out
    assert "dry-run" in out


def test_cmd_rotate_falls_back_to_existing_recipients(mock_config: EnvaultConfig):
    with (
        patch("envault.cli_rotate._load_config", return_value=mock_config),
        patch("envault.cli_rotate.passphrase_from_env", return_value=None),
        patch("envault.cli_rotate.rotate", return_value=Path(".env.gpg")) as mock_rotate,
    ):
        cmd_rotate(_ns(recipient=[]))  # no --recipient flags

    _, kwargs = mock_rotate.call_args
    assert kwargs["new_recipients"] == list(mock_config.recipients)


def test_cmd_rotate_exits_on_rotation_error(mock_config: EnvaultConfig):
    with (
        patch("envault.cli_rotate._load_config", return_value=mock_config),
        patch("envault.cli_rotate.passphrase_from_env", return_value=None),
        patch("envault.cli_rotate.rotate", side_effect=RotationError("boom")),
        pytest.raises(SystemExit) as exc_info,
    ):
        cmd_rotate(_ns())

    assert exc_info.value.code == 1


def test_cmd_rotate_error_message_printed(mock_config: EnvaultConfig, capsys):
    """Ensure the RotationError message is surfaced to stderr on failure."""
    with (
        patch("envault.cli_rotate._load_config", return_value=mock_config),
        patch("envault.cli_rotate.passphrase_from_env", return_value=None),
        patch("envault.cli_rotate.rotate", side_effect=RotationError("boom")),
        pytest.raises(SystemExit),
    ):
        cmd_rotate(_ns())

    err = capsys.readouterr().err
    assert "boom" in err


def test_register_subcommand_adds_rotate():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_subcommand(sub)
    args = parser.parse_args(["rotate", "--dry-run", "-r", "KEY1"])
    assert args.dry_run is True
    assert args.recipient == ["KEY1"]
