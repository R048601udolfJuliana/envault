"""Tests for envault.cli_cast."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from envault.cli_cast import cmd_cast, register_subcommand


def _ns(**kwargs) -> argparse.Namespace:
    defaults = {"config": ".envault.json", "file": None, "hint": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture()
def mock_config(tmp_path: Path):
    cfg = MagicMock()
    cfg.env_file = str(tmp_path / ".env")
    return cfg


def test_register_subcommand_adds_cast_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_subcommand(sub)
    args = parser.parse_args(["cast"])
    assert hasattr(args, "func")


def test_cmd_cast_success(tmp_path: Path, mock_config, capsys):
    env = tmp_path / ".env"
    env.write_text("PORT=9000\nDEBUG=true\n", encoding="utf-8")
    mock_config.env_file = str(env)

    with patch("envault.cli_cast.EnvaultConfig.load", return_value=mock_config):
        cmd_cast(_ns(hint=["PORT:int", "DEBUG:bool"]))

    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["PORT"] == 9000
    assert data["DEBUG"] is True


def test_cmd_cast_config_error_exits(tmp_path: Path):
    from envault.config import ConfigError

    with patch("envault.cli_cast.EnvaultConfig.load", side_effect=ConfigError("boom")):
        with pytest.raises(SystemExit) as exc:
            cmd_cast(_ns())
    assert exc.value.code == 1


def test_cmd_cast_cast_error_exits(tmp_path: Path, mock_config):
    from envault.env_cast import CastError

    with patch("envault.cli_cast.EnvaultConfig.load", return_value=mock_config):
        with patch("envault.cli_cast.cast_env", side_effect=CastError("bad cast")):
            with pytest.raises(SystemExit) as exc:
                cmd_cast(_ns())
    assert exc.value.code == 1


def test_cmd_cast_invalid_hint_format_exits(tmp_path: Path, mock_config):
    with patch("envault.cli_cast.EnvaultConfig.load", return_value=mock_config):
        with pytest.raises(SystemExit) as exc:
            cmd_cast(_ns(hint=["BADFORMAT"]))
    assert exc.value.code == 1


def test_cmd_cast_uses_explicit_file(tmp_path: Path, mock_config, capsys):
    env = tmp_path / "custom.env"
    env.write_text("X=42\n", encoding="utf-8")

    with patch("envault.cli_cast.EnvaultConfig.load", return_value=mock_config):
        cmd_cast(_ns(file=str(env), hint=["X:int"]))

    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["X"] == 42
