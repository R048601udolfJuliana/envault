"""Tests for envault.import_env and envault.cli_import."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from envault.import_env import import_env, ImportError, _parse_env
from envault.cli_import import cmd_import


# ---------------------------------------------------------------------------
# _parse_env
# ---------------------------------------------------------------------------

def test_parse_env_basic():
    text = "FOO=bar\nBAZ=qux\n"
    assert _parse_env(text) == {"FOO": "bar", "BAZ": "qux"}


def test_parse_env_strips_quotes():
    text = 'KEY="hello world"\nOTHER=\'value\'\n'
    result = _parse_env(text)
    assert result["KEY"] == "hello world"
    assert result["OTHER"] == "value"


def test_parse_env_ignores_comments_and_blanks():
    text = "# comment\n\nFOO=1\n"
    assert _parse_env(text) == {"FOO": "1"}


def test_parse_env_skips_lines_without_equals():
    text = "NOEQUALSSIGN\nFOO=bar\n"
    assert _parse_env(text) == {"FOO": "bar"}


# ---------------------------------------------------------------------------
# import_env
# ---------------------------------------------------------------------------

@pytest.fixture()
def config(tmp_path: Path):
    enc = tmp_path / ".env.gpg"
    enc.write_bytes(b"fake-encrypted")
    cfg = MagicMock()
    cfg.encrypted_file = str(enc)
    return cfg


def test_import_env_sets_os_environ(config, monkeypatch):
    monkeypatch.delenv("MY_KEY", raising=False)
    with patch("envault.import_env.decrypt_file", return_value="MY_KEY=secret\n"):
        result = import_env(config)
    assert result == {"MY_KEY": "secret"}
    assert os.environ["MY_KEY"] == "secret"


def test_import_env_dry_run_does_not_set_environ(config, monkeypatch):
    monkeypatch.delenv("DRY_KEY", raising=False)
    with patch("envault.import_env.decrypt_file", return_value="DRY_KEY=dryval\n"):
        result = import_env(config, dry_run=True)
    assert result == {"DRY_KEY": "dryval"}
    assert "DRY_KEY" not in os.environ


def test_import_env_skips_existing_without_overwrite(config, monkeypatch):
    monkeypatch.setenv("EXIST_KEY", "original")
    with patch("envault.import_env.decrypt_file", return_value="EXIST_KEY=new\n"):
        result = import_env(config, overwrite=False)
    assert result == {}
    assert os.environ["EXIST_KEY"] == "original"


def test_import_env_overwrites_when_flag_set(config, monkeypatch):
    monkeypatch.setenv("OVER_KEY", "old")
    with patch("envault.import_env.decrypt_file", return_value="OVER_KEY=new\n"):
        result = import_env(config, overwrite=True)
    assert result == {"OVER_KEY": "new"}
    assert os.environ["OVER_KEY"] == "new"


def test_import_env_raises_when_encrypted_file_missing(tmp_path):
    cfg = MagicMock()
    cfg.encrypted_file = str(tmp_path / "nonexistent.gpg")
    with pytest.raises(ImportError, match="Encrypted file not found"):
        import_env(cfg)


def test_import_env_raises_on_specific_key_missing(config):
    with patch("envault.import_env.decrypt_file", return_value="FOO=1\n"):
        with pytest.raises(ImportError, match="MISSING"):
            import_env(config, keys=["MISSING"])


# ---------------------------------------------------------------------------
# cmd_import (CLI)
# ---------------------------------------------------------------------------

def _ns(**kwargs):
    defaults = {
        "config": ".envault.json",
        "overwrite": False,
        "dry_run": False,
        "keys": [],
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_import_success(capsys):
    mock_cfg = MagicMock()
    with patch("envault.cli_import.EnvaultConfig.load", return_value=mock_cfg), \
         patch("envault.cli_import.passphrase_from_env", return_value=None), \
         patch("envault.cli_import.import_env", return_value={"A": "1", "B": "2"}):
        cmd_import(_ns())
    out = capsys.readouterr().out
    assert "Imported: A" in out
    assert "2 variable(s) imported" in out


def test_cmd_import_nothing_to_import(capsys):
    mock_cfg = MagicMock()
    with patch("envault.cli_import.EnvaultConfig.load", return_value=mock_cfg), \
         patch("envault.cli_import.passphrase_from_env", return_value=None), \
         patch("envault.cli_import.import_env", return_value={}):
        cmd_import(_ns())
    out = capsys.readouterr().out
    assert "nothing to import" in out


def test_cmd_import_error_exits(capsys):
    with patch("envault.cli_import.EnvaultConfig.load", side_effect=Exception("bad config")), \
         pytest.raises(SystemExit):
        cmd_import(_ns())
