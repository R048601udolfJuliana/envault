"""Tests for envault.cli_prefix."""
from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from envault.cli_prefix import cmd_prefix_add, cmd_prefix_strip


def _ns(**kwargs) -> argparse.Namespace:
    defaults = {
        "prefix": "APP_",
        "file": "",
        "dest": "",
        "config": ".envault.json",
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture()
def mock_config(tmp_path: Path):
    cfg = MagicMock()
    cfg.env_file = str(tmp_path / ".env")
    return cfg


def test_cmd_prefix_add_success(tmp_path: Path, mock_config) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=val\n")
    with patch("envault.cli_prefix.EnvaultConfig.load", return_value=mock_config), \
         patch("envault.cli_prefix.add_prefix", return_value=env_file) as mock_add:
        cmd_prefix_add(_ns(file=str(env_file)))
    mock_add.assert_called_once()


def test_cmd_prefix_add_error_exits(tmp_path: Path, mock_config) -> None:
    from envault.env_prefix import PrefixError
    with patch("envault.cli_prefix.EnvaultConfig.load", return_value=mock_config), \
         patch("envault.cli_prefix.add_prefix", side_effect=PrefixError("bad")):
        with pytest.raises(SystemExit) as exc:
            cmd_prefix_add(_ns(file=str(tmp_path / ".env")))
    assert exc.value.code == 1


def test_cmd_prefix_strip_success(tmp_path: Path, mock_config) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("APP_KEY=val\n")
    with patch("envault.cli_prefix.EnvaultConfig.load", return_value=mock_config), \
         patch("envault.cli_prefix.strip_prefix", return_value=env_file) as mock_strip:
        cmd_prefix_strip(_ns(file=str(env_file)))
    mock_strip.assert_called_once()


def test_cmd_prefix_strip_error_exits(tmp_path: Path, mock_config) -> None:
    from envault.env_prefix import PrefixError
    with patch("envault.cli_prefix.EnvaultConfig.load", return_value=mock_config), \
         patch("envault.cli_prefix.strip_prefix", side_effect=PrefixError("oops")):
        with pytest.raises(SystemExit) as exc:
            cmd_prefix_strip(_ns(file=str(tmp_path / ".env")))
    assert exc.value.code == 1


def test_cmd_prefix_add_uses_config_env_file(tmp_path: Path, mock_config) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=val\n")
    mock_config.env_file = str(env_file)
    with patch("envault.cli_prefix.EnvaultConfig.load", return_value=mock_config), \
         patch("envault.cli_prefix.add_prefix", return_value=env_file) as mock_add:
        cmd_prefix_add(_ns())  # no --file provided
    called_src = mock_add.call_args[0][0]
    assert called_src == Path(mock_config.env_file)
