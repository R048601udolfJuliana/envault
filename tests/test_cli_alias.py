"""Tests for envault.cli_alias."""
import sys
import types
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from envault.cli_alias import (
    cmd_alias_add,
    cmd_alias_list,
    cmd_alias_remove,
    cmd_alias_resolve,
)


def _ns(**kwargs):
    ns = types.SimpleNamespace(**kwargs)
    return ns


@pytest.fixture
def mock_config(tmp_path):
    cfg = MagicMock()
    cfg.config_path = str(tmp_path / ".envault.json")
    return cfg


def test_cmd_alias_add_success(mock_config, capsys):
    args = _ns(name="dev", target="development", force=False)
    cmd_alias_add(args, mock_config)
    out = capsys.readouterr().out
    assert "dev" in out
    assert "development" in out


def test_cmd_alias_add_duplicate_exits(mock_config):
    args = _ns(name="dev", target="development", force=False)
    cmd_alias_add(args, mock_config)
    with pytest.raises(SystemExit):
        cmd_alias_add(_ns(name="dev", target="other", force=False), mock_config)


def test_cmd_alias_add_force_overwrites(mock_config, capsys):
    args = _ns(name="dev", target="development", force=False)
    cmd_alias_add(args, mock_config)
    args2 = _ns(name="dev", target="dev-new", force=True)
    cmd_alias_add(args2, mock_config)
    out = capsys.readouterr().out
    assert "dev-new" in out


def test_cmd_alias_remove_success(mock_config, capsys):
    cmd_alias_add(_ns(name="x", target="y", force=False), mock_config)
    cmd_alias_remove(_ns(name="x"), mock_config)
    out = capsys.readouterr().out
    assert "removed" in out


def test_cmd_alias_remove_not_found_exits(mock_config):
    with pytest.raises(SystemExit):
        cmd_alias_remove(_ns(name="ghost"), mock_config)


def test_cmd_alias_list_empty(mock_config, capsys):
    cmd_alias_list(_ns(), mock_config)
    out = capsys.readouterr().out
    assert "No aliases" in out


def test_cmd_alias_list_shows_entries(mock_config, capsys):
    cmd_alias_add(_ns(name="prod", target="production", force=False), mock_config)
    cmd_alias_list(_ns(), mock_config)
    out = capsys.readouterr().out
    assert "prod" in out
    assert "production" in out


def test_cmd_alias_resolve_success(mock_config, capsys):
    cmd_alias_add(_ns(name="s", target="staging", force=False), mock_config)
    cmd_alias_resolve(_ns(name="s"), mock_config)
    out = capsys.readouterr().out
    assert "staging" in out


def test_cmd_alias_resolve_missing_exits(mock_config):
    with pytest.raises(SystemExit):
        cmd_alias_resolve(_ns(name="nope"), mock_config)
