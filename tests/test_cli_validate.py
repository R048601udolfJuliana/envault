"""Tests for envault.cli_validate"""
import argparse
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from envault.cli_validate import cmd_validate, register_subcommand
from envault.env_validate import ValidationResult, ValidationIssue


def _ns(**kwargs):
    defaults = dict(config=".envault.json", require=None, pattern=None, strict=False)
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture
def mock_config(tmp_path):
    cfg = MagicMock()
    cfg.env_file = tmp_path / ".env"
    return cfg


def test_cmd_validate_success(mock_config, capsys):
    ok_result = ValidationResult()
    with patch("envault.cli_validate._load_config", return_value=mock_config), \
         patch("envault.cli_validate.validate_env", return_value=ok_result):
        cmd_validate(_ns(require=["KEY"]))
    out = capsys.readouterr().out
    assert "All required" in out


def test_cmd_validate_issues_no_strict(mock_config, capsys):
    result = ValidationResult(issues=[ValidationIssue("KEY", "missing required key")])
    with patch("envault.cli_validate._load_config", return_value=mock_config), \
         patch("envault.cli_validate.validate_env", return_value=result):
        cmd_validate(_ns(require=["KEY"], strict=False))
    out = capsys.readouterr().out
    assert "KEY" in out


def test_cmd_validate_issues_strict_exits(mock_config):
    result = ValidationResult(issues=[ValidationIssue("KEY", "missing required key")])
    with patch("envault.cli_validate._load_config", return_value=mock_config), \
         patch("envault.cli_validate.validate_env", return_value=result):
        with pytest.raises(SystemExit) as exc:
            cmd_validate(_ns(require=["KEY"], strict=True))
        assert exc.value.code == 1


def test_cmd_validate_config_error_exits():
    from envault.config import ConfigError
    with patch("envault.cli_validate._load_config", side_effect=ConfigError("bad")):
        with pytest.raises(SystemExit) as exc:
            cmd_validate(_ns())
        assert exc.value.code == 1


def test_cmd_validate_invalid_pattern_exits(mock_config):
    with patch("envault.cli_validate._load_config", return_value=mock_config):
        with pytest.raises(SystemExit) as exc:
            cmd_validate(_ns(pattern=["NOCODON"]))
        assert exc.value.code == 1


def test_register_subcommand_adds_parser():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers()
    register_subcommand(subs)
    args = parser.parse_args(["validate"])
    assert hasattr(args, "func")
