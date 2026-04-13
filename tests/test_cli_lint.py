"""Tests for envault.cli_lint."""

from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import patch

import pytest

from envault.cli_lint import cmd_lint, register_subcommand
from envault.lint import LintError, LintResult, LintIssue


def _ns(**kwargs) -> argparse.Namespace:
    defaults = {"file": ".env", "strict": False}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_lint_clean_file(tmp_path: Path, capsys) -> None:
    env = tmp_path / ".env"
    env.write_text("FOO=bar\n")
    cmd_lint(_ns(file=str(env)))
    out = capsys.readouterr().out
    assert "No issues found" in out


def test_cmd_lint_with_issues_no_strict(tmp_path: Path, capsys) -> None:
    env = tmp_path / ".env"
    env.write_text("EMPTY=\n")
    cmd_lint(_ns(file=str(env), strict=False))
    out = capsys.readouterr().out
    assert "issue(s) found" in out


def test_cmd_lint_with_issues_strict_exits(tmp_path: Path) -> None:
    env = tmp_path / ".env"
    env.write_text("EMPTY=\n")
    with pytest.raises(SystemExit) as exc_info:
        cmd_lint(_ns(file=str(env), strict=True))
    assert exc_info.value.code == 1


def test_cmd_lint_missing_file_exits(tmp_path: Path) -> None:
    with pytest.raises(SystemExit) as exc_info:
        cmd_lint(_ns(file=str(tmp_path / "missing.env")))
    assert exc_info.value.code == 1


def test_register_subcommand_creates_parser() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    register_subcommand(subparsers)
    args = parser.parse_args(["lint", ".env"])
    assert args.file == ".env"
    assert args.strict is False


def test_register_subcommand_strict_flag() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    register_subcommand(subparsers)
    args = parser.parse_args(["lint", "--strict"])
    assert args.strict is True
