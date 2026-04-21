"""Tests for envault.cli_annotate."""
from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from envault.cli_annotate import cmd_annotate_list, cmd_annotate_set


def _ns(**kwargs) -> argparse.Namespace:
    defaults = {"config": ".envault.json", "key": "DB_HOST", "type": "", "desc": "", "dest": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture()
def mock_config(tmp_path: Path):
    cfg = MagicMock()
    cfg.env_file = str(tmp_path / ".env")
    with patch("envault.cli_annotate._load_config", return_value=cfg):
        yield cfg, tmp_path


def test_cmd_annotate_set_success(mock_config, capsys):
    cfg, tmp_path = mock_config
    env = tmp_path / ".env"
    env.write_text("DB_HOST=localhost\n")
    with patch("envault.cli_annotate.annotate_key", return_value=env) as mock_ann:
        cmd_annotate_set(_ns(key="DB_HOST", type="string", desc="host"))
        mock_ann.assert_called_once()
    out = capsys.readouterr().out
    assert "annotation written" in out


def test_cmd_annotate_set_error_exits(mock_config):
    with patch("envault.cli_annotate.annotate_key", side_effect=Exception("boom")):
        with pytest.raises(SystemExit):
            cmd_annotate_set(_ns(key="MISSING", type="string"))


def test_cmd_annotate_list_no_annotations(mock_config, capsys):
    cfg, tmp_path = mock_config
    with patch("envault.cli_annotate.read_annotations", return_value={}):
        cmd_annotate_list(_ns())
    out = capsys.readouterr().out
    assert "No annotations" in out


def test_cmd_annotate_list_with_entries(mock_config, capsys):
    annotations = {"DB_HOST": {"type": "string", "desc": "host"}}
    with patch("envault.cli_annotate.read_annotations", return_value=annotations):
        cmd_annotate_list(_ns())
    out = capsys.readouterr().out
    assert "DB_HOST" in out
    assert "type=string" in out
    assert "desc=host" in out


def test_cmd_annotate_list_error_exits(mock_config):
    from envault.env_annotate import AnnotateError
    with patch("envault.cli_annotate.read_annotations", side_effect=AnnotateError("bad")):
        with pytest.raises(SystemExit):
            cmd_annotate_list(_ns())
