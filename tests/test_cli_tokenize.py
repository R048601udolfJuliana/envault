"""Tests for envault.cli_tokenize."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from envault.cli_tokenize import cmd_tokenize, register_subcommand
from envault.env_tokenize import TokenizeError, TokenizeResult, TokenizedEntry


def _ns(**kwargs) -> SimpleNamespace:
    defaults = {"config": None, "file": None, "type": None, "summary": False}
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


@pytest.fixture()
def mock_config(tmp_path):
    cfg = MagicMock()
    cfg.env_file = str(tmp_path / ".env")
    return cfg


def _make_result(*entries):
    return TokenizeResult(entries=list(entries))


def test_cmd_tokenize_success(mock_config, capsys):
    result = _make_result(
        TokenizedEntry(key="PORT", raw_value="8080", token_type="integer"),
        TokenizedEntry(key="URL", raw_value="https://x.com", token_type="url"),
    )
    with patch("envault.cli_tokenize._load_config", return_value=mock_config), \
         patch("envault.cli_tokenize.tokenize_env", return_value=result):
        cmd_tokenize(_ns())
    out = capsys.readouterr().out
    assert "PORT" in out
    assert "URL" in out


def test_cmd_tokenize_filter_by_type(mock_config, capsys):
    result = _make_result(
        TokenizedEntry(key="PORT", raw_value="8080", token_type="integer"),
        TokenizedEntry(key="URL", raw_value="https://x.com", token_type="url"),
    )
    with patch("envault.cli_tokenize._load_config", return_value=mock_config), \
         patch("envault.cli_tokenize.tokenize_env", return_value=result):
        cmd_tokenize(_ns(type="url"))
    out = capsys.readouterr().out
    assert "URL" in out
    assert "PORT" not in out


def test_cmd_tokenize_summary(mock_config, capsys):
    result = _make_result(
        TokenizedEntry(key="PORT", raw_value="8080", token_type="integer"),
    )
    with patch("envault.cli_tokenize._load_config", return_value=mock_config), \
         patch("envault.cli_tokenize.tokenize_env", return_value=result):
        cmd_tokenize(_ns(summary=True))
    out = capsys.readouterr().out
    assert "Total keys" in out


def test_cmd_tokenize_error_exits(mock_config, capsys):
    with patch("envault.cli_tokenize._load_config", return_value=mock_config), \
         patch("envault.cli_tokenize.tokenize_env", side_effect=TokenizeError("bad file")), \
         pytest.raises(SystemExit) as exc_info:
        cmd_tokenize(_ns())
    assert exc_info.value.code == 1
    assert "bad file" in capsys.readouterr().err


def test_register_subcommand_adds_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_subcommand(sub)
    args = parser.parse_args(["tokenize", "--summary"])
    assert args.summary is True
