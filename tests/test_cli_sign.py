"""Tests for envault.cli_sign."""
from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from envault.cli_sign import cmd_sign, cmd_verify_sig, register_subcommands


def _ns(**kwargs):
    defaults = {"config": ".envault.json", "key_id": "ABCD1234", "sig": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture()
def mock_config(tmp_path):
    cfg = MagicMock()
    cfg.encrypted_file = str(tmp_path / "vault.env.gpg")
    return cfg


def test_cmd_sign_success(mock_config, tmp_path, capsys):
    Path(mock_config.encrypted_file).write_bytes(b"data")
    sig_path = Path(mock_config.encrypted_file + ".sig")
    with patch("envault.cli_sign._load_config", return_value=mock_config), \
         patch("envault.cli_sign.sign_file", return_value=sig_path) as mock_sign:
        cmd_sign(_ns())
    mock_sign.assert_called_once()
    out = capsys.readouterr().out
    assert "Signed" in out


def test_cmd_sign_error_exits(mock_config):
    from envault.sign import SignError
    with patch("envault.cli_sign._load_config", return_value=mock_config), \
         patch("envault.cli_sign.sign_file", side_effect=SignError("fail")):
        with pytest.raises(SystemExit) as exc:
            cmd_sign(_ns())
    assert exc.value.code == 1


def test_cmd_verify_sig_success(mock_config, capsys):
    with patch("envault.cli_sign._load_config", return_value=mock_config), \
         patch("envault.cli_sign.verify_signature", return_value="DEADBEEF"):
        cmd_verify_sig(_ns())
    out = capsys.readouterr().out
    assert "valid" in out
    assert "DEADBEEF" in out


def test_cmd_verify_sig_error_exits(mock_config):
    from envault.sign import SignError
    with patch("envault.cli_sign._load_config", return_value=mock_config), \
         patch("envault.cli_sign.verify_signature", side_effect=SignError("bad")):
        with pytest.raises(SystemExit) as exc:
            cmd_verify_sig(_ns())
    assert exc.value.code == 1


def test_register_subcommands_adds_parsers():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_subcommands(sub)
    args = parser.parse_args(["sign", "--key-id", "ABC"])
    assert hasattr(args, "func")
