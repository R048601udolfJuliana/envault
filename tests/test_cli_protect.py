"""Tests for envault.cli_protect."""
from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from envault.cli_protect import (
    cmd_protect_add,
    cmd_protect_list,
    cmd_protect_remove,
)


def _ns(**kwargs) -> argparse.Namespace:  # type: ignore[return]
    defaults = {"config": ".envault.json"}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture()
def mock_config(tmp_path: Path):
    cfg = MagicMock()
    cfg.vault_dir = str(tmp_path)
    return cfg


def test_cmd_protect_add_success(mock_config, capsys):
    ns = _ns(key="DB_PASSWORD")
    with patch("envault.cli_protect._load_config", return_value=mock_config), \
         patch("envault.cli_protect.protect_key") as mock_protect:
        cmd_protect_add(ns)
    mock_protect.assert_called_once()
    out = capsys.readouterr().out
    assert "DB_PASSWORD" in out
    assert "protected" in out


def test_cmd_protect_add_error_exits(mock_config, capsys):
    from envault.env_protect import ProtectError
    ns = _ns(key="DB_PASSWORD")
    with patch("envault.cli_protect._load_config", return_value=mock_config), \
         patch("envault.cli_protect.protect_key", side_effect=ProtectError("oops")), \
         pytest.raises(SystemExit) as exc:
        cmd_protect_add(ns)
    assert exc.value.code == 1


def test_cmd_protect_remove_success(mock_config, capsys):
    ns = _ns(key="SECRET")
    with patch("envault.cli_protect._load_config", return_value=mock_config), \
         patch("envault.cli_protect.unprotect_key") as mock_unprotect:
        cmd_protect_remove(ns)
    mock_unprotect.assert_called_once()
    out = capsys.readouterr().out
    assert "SECRET" in out


def test_cmd_protect_remove_not_found_exits(mock_config, capsys):
    from envault.env_protect import ProtectError
    ns = _ns(key="MISSING")
    with patch("envault.cli_protect._load_config", return_value=mock_config), \
         patch("envault.cli_protect.unprotect_key", side_effect=ProtectError("not protected")), \
         pytest.raises(SystemExit) as exc:
        cmd_protect_remove(ns)
    assert exc.value.code == 1


def test_cmd_protect_list_empty(mock_config, capsys):
    ns = _ns()
    with patch("envault.cli_protect._load_config", return_value=mock_config), \
         patch("envault.cli_protect.load_protected", return_value=[]):
        cmd_protect_list(ns)
    out = capsys.readouterr().out
    assert "No keys" in out


def test_cmd_protect_list_shows_keys(mock_config, capsys):
    ns = _ns()
    with patch("envault.cli_protect._load_config", return_value=mock_config), \
         patch("envault.cli_protect.load_protected", return_value=["API_KEY", "DB_PASS"]):
        cmd_protect_list(ns)
    out = capsys.readouterr().out
    assert "API_KEY" in out
    assert "DB_PASS" in out
