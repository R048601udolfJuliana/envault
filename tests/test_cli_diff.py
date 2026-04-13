"""Tests for envault.cli_diff."""
import argparse
from pathlib import Path
from unittest.mock import patch

import pytest

from envault.cli_diff import cmd_diff, register_subcommand
from envault.diff import DiffError, EnvDiff


def _ns(**kwargs) -> argparse.Namespace:
    defaults = {"old": "old.env", "new": "new.env", "unified": False, "exit_code": False}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_diff_no_changes(capsys):
    diff_result = EnvDiff()
    with patch("envault.cli_diff.diff_env_files", return_value=diff_result):
        rc = cmd_diff(_ns())
    assert rc == 0
    out = capsys.readouterr().out
    assert "No changes" in out


def test_cmd_diff_with_changes_exit_code_zero_by_default(capsys):
    diff_result = EnvDiff(added=["NEW_KEY"])
    with patch("envault.cli_diff.diff_env_files", return_value=diff_result):
        rc = cmd_diff(_ns())
    assert rc == 0
    out = capsys.readouterr().out
    assert "+ NEW_KEY" in out


def test_cmd_diff_with_changes_exit_code_flag(capsys):
    diff_result = EnvDiff(removed=["OLD_KEY"])
    with patch("envault.cli_diff.diff_env_files", return_value=diff_result):
        rc = cmd_diff(_ns(exit_code=True))
    assert rc == 1


def test_cmd_diff_unified_output(capsys):
    with patch("envault.cli_diff.unified_diff", return_value="-FOO=1\n+FOO=2\n"):
        rc = cmd_diff(_ns(unified=True))
    assert rc == 0
    out = capsys.readouterr().out
    assert "-FOO=1" in out


def test_cmd_diff_unified_no_changes(capsys):
    with patch("envault.cli_diff.unified_diff", return_value=""):
        rc = cmd_diff(_ns(unified=True))
    assert rc == 0
    out = capsys.readouterr().out
    assert "No changes" in out


def test_cmd_diff_diff_error(capsys):
    with patch("envault.cli_diff.diff_env_files", side_effect=DiffError("file missing")):
        rc = cmd_diff(_ns())
    assert rc == 2
    err = capsys.readouterr().err
    assert "file missing" in err


def test_register_subcommand_registers_diff():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers()
    register_subcommand(subs)
    args = parser.parse_args(["diff", "a.env", "b.env"])
    assert args.old == "a.env"
    assert args.new == "b.env"
    assert args.unified is False
    assert args.exit_code is False
    assert callable(args.func)
