"""Tests for envault.cli_encode."""
from __future__ import annotations

import argparse
import base64
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from envault.cli_encode import cmd_decode, cmd_encode


def _ns(**kwargs) -> argparse.Namespace:
    defaults = {'config': '.envault.json', 'dest': None, 'keys': None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture()
def mock_config(tmp_path: Path):
    env_file = tmp_path / '.env'
    env_file.write_text('API=secret\n')
    cfg = MagicMock()
    cfg.env_file = str(env_file)
    return cfg


def test_cmd_encode_success(mock_config, capsys) -> None:
    with patch('envault.cli_encode._load_config', return_value=mock_config):
        cmd_encode(_ns())
    out = capsys.readouterr().out
    assert 'encoded' in out


def test_cmd_encode_error_exits(mock_config) -> None:
    with patch('envault.cli_encode._load_config', return_value=mock_config):
        with patch('envault.cli_encode.encode_env', side_effect=Exception('boom')):
            with pytest.raises(SystemExit) as exc_info:
                cmd_encode(_ns())
    assert exc_info.value.code == 1


def test_cmd_encode_config_error_exits() -> None:
    from envault.config import ConfigError
    with patch('envault.cli_encode._load_config', side_effect=ConfigError('bad')):
        with pytest.raises(SystemExit) as exc_info:
            cmd_encode(_ns())
    assert exc_info.value.code == 1


def test_cmd_decode_success(mock_config, capsys, tmp_path) -> None:
    env_file = Path(mock_config.env_file)
    encoded = base64.b64encode(b'secret').decode()
    env_file.write_text(f'API={encoded}\n')
    with patch('envault.cli_encode._load_config', return_value=mock_config):
        cmd_decode(_ns())
    out = capsys.readouterr().out
    assert 'decoded' in out


def test_cmd_decode_error_exits(mock_config) -> None:
    from envault.env_encode import EncodeError
    with patch('envault.cli_encode._load_config', return_value=mock_config):
        with patch('envault.cli_encode.decode_env', side_effect=EncodeError('bad')):
            with pytest.raises(SystemExit) as exc_info:
                cmd_decode(_ns())
    assert exc_info.value.code == 1


def test_register_subcommands_adds_parsers() -> None:
    from envault.cli_encode import register_subcommands
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_subcommands(sub)
    ns = parser.parse_args(['encode', '--dest', '/tmp/out'])
    assert ns.dest == '/tmp/out'
    ns2 = parser.parse_args(['decode', '--keys', 'A', 'B'])
    assert ns2.keys == ['A', 'B']
