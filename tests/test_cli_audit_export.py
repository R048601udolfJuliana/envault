"""Tests for envault.cli_audit_export."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from envault.cli_audit_export import cmd_audit_export, register_subcommand
from envault.config import ConfigError
from envault.env_audit_export import AuditExportError


def _ns(**kwargs) -> argparse.Namespace:  # type: ignore[type-arg]
    defaults = {
        "config": ".envault.json",
        "output": "audit_export.json",
        "format": "json",
        "limit": None,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture()
def mock_config(tmp_path: Path) -> MagicMock:
    cfg = MagicMock()
    cfg.base_dir = str(tmp_path)
    return cfg


def test_cmd_audit_export_success(tmp_path: Path, mock_config: MagicMock, capsys) -> None:
    args = _ns(output=str(tmp_path / "out.json"))
    with patch("envault.cli_audit_export._load_config", return_value=mock_config), \
         patch("envault.cli_audit_export.export_audit", return_value=5) as mock_exp:
        cmd_audit_export(args)
    mock_exp.assert_called_once()
    captured = capsys.readouterr()
    assert "5" in captured.out


def test_cmd_audit_export_config_error_exits(tmp_path: Path) -> None:
    args = _ns(output=str(tmp_path / "out.json"))
    with patch("envault.cli_audit_export._load_config", side_effect=ConfigError("bad cfg")):
        with pytest.raises(SystemExit) as exc:
            cmd_audit_export(args)
    assert exc.value.code == 1


def test_cmd_audit_export_error_exits(tmp_path: Path, mock_config: MagicMock, capsys) -> None:
    args = _ns(output=str(tmp_path / "out.json"))
    with patch("envault.cli_audit_export._load_config", return_value=mock_config), \
         patch("envault.cli_audit_export.export_audit", side_effect=AuditExportError("no entries")):
        with pytest.raises(SystemExit) as exc:
            cmd_audit_export(args)
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "no entries" in captured.err


def test_register_subcommand_adds_parser() -> None:
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers()
    register_subcommand(subs)
    ns = parser.parse_args(["audit-export", "out.json", "--format", "csv", "--limit", "10"])
    assert ns.output == "out.json"
    assert ns.format == "csv"
    assert ns.limit == 10
