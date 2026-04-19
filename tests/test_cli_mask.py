"""Tests for envault.cli_mask."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from envault.cli_mask import cmd_mask


def _ns(**kwargs):
    defaults = {
        "config": ".envault.json",
        "source": None,
        "output": None,
        "keys": None,
        "placeholder": "***",
        "no_auto": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture()
def mock_config(tmp_path):
    cfg = MagicMock()
    cfg.env_file = str(tmp_path / ".env")
    return cfg


def test_cmd_mask_success(tmp_path, mock_config, capsys):
    env = tmp_path / ".env"
    env.write_text("API_KEY=secret\nNAME=alice\n")
    mock_config.env_file = str(env)

    with patch("envault.cli_mask._load_config", return_value=mock_config):
        cmd_mask(_ns())

    out = capsys.readouterr().out
    assert "Masked" in out
    assert "API_KEY" in out


def test_cmd_mask_no_sensitive_keys(tmp_path, mock_config, capsys):
    env = tmp_path / ".env"
    env.write_text("NAME=alice\n")
    mock_config.env_file = str(env)

    with patch("envault.cli_mask._load_config", return_value=mock_config):
        cmd_mask(_ns())

    out = capsys.readouterr().out
    assert "No sensitive" in out


def test_cmd_mask_error_exits(tmp_path, mock_config):
    mock_config.env_file = str(tmp_path / "missing.env")

    with patch("envault.cli_mask._load_config", return_value=mock_config):
        with pytest.raises(SystemExit) as exc:
            cmd_mask(_ns())
    assert exc.value.code == 1


def test_cmd_mask_output_reported(tmp_path, mock_config, capsys):
    env = tmp_path / ".env"
    env.write_text("SECRET=val\n")
    mock_config.env_file = str(env)
    out_file = tmp_path / "out.env"

    with patch("envault.cli_mask._load_config", return_value=mock_config):
        cmd_mask(_ns(output=str(out_file)))

    output = capsys.readouterr().out
    assert str(out_file) in output
