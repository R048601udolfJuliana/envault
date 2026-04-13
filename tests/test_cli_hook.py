"""Tests for envault.cli_hook."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from envault.cli_hook import cmd_hook_install, cmd_hook_uninstall, cmd_hook_status
from envault.hook import HookError


def _ns(**kwargs) -> argparse.Namespace:
    defaults = {"repo": None, "force": False}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_hook_install_success(tmp_path: Path, capsys) -> None:
    with patch("envault.cli_hook.install_hook", return_value=Path("/repo/.git/hooks/pre-commit")) as m:
        cmd_hook_install(_ns())
    m.assert_called_once()
    out = capsys.readouterr().out
    assert "installed" in out.lower()


def test_cmd_hook_install_force_passed(tmp_path: Path) -> None:
    with patch("envault.cli_hook.install_hook", return_value=Path("/x")) as m:
        cmd_hook_install(_ns(force=True))
    _, kwargs = m.call_args
    assert m.call_args[0][1] is True or kwargs.get("force") is True


def test_cmd_hook_install_error_exits(capsys) -> None:
    with patch("envault.cli_hook.install_hook", side_effect=HookError("already exists")):
        with pytest.raises(SystemExit) as exc_info:
            cmd_hook_install(_ns())
    assert exc_info.value.code == 1
    assert "already exists" in capsys.readouterr().err


def test_cmd_hook_uninstall_success(capsys) -> None:
    with patch("envault.cli_hook.uninstall_hook") as m:
        cmd_hook_uninstall(_ns())
    m.assert_called_once()
    assert "removed" in capsys.readouterr().out.lower()


def test_cmd_hook_uninstall_error_exits(capsys) -> None:
    with patch("envault.cli_hook.uninstall_hook", side_effect=HookError("No hook found")):
        with pytest.raises(SystemExit) as exc_info:
            cmd_hook_uninstall(_ns())
    assert exc_info.value.code == 1


def test_cmd_hook_status_output(capsys) -> None:
    fake_status = {"installed": True, "envault_managed": True, "path": "/repo/.git/hooks/pre-commit"}
    with patch("envault.cli_hook.hook_status", return_value=fake_status):
        cmd_hook_status(_ns())
    out = capsys.readouterr().out
    assert "True" in out
    assert "/repo/.git/hooks/pre-commit" in out
