"""Tests for envault.cli_schedule."""
from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import patch

import pytest

from envault.cli_schedule import (
    cmd_schedule_check,
    cmd_schedule_delete,
    cmd_schedule_set,
    cmd_schedule_show,
)


def _ns(**kwargs):
    defaults = {"config_dir": "."}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_schedule_set_success(tmp_path, capsys):
    ns = _ns(config_dir=str(tmp_path), days=5)
    cmd_schedule_set(ns)
    out = capsys.readouterr().out
    assert "5" in out


def test_cmd_schedule_set_invalid_exits(tmp_path):
    ns = _ns(config_dir=str(tmp_path), days=0)
    with pytest.raises(SystemExit) as exc:
        cmd_schedule_set(ns)
    assert exc.value.code == 1


def test_cmd_schedule_show_no_schedule(tmp_path, capsys):
    ns = _ns(config_dir=str(tmp_path))
    cmd_schedule_show(ns)
    assert "No schedule" in capsys.readouterr().out


def test_cmd_schedule_show_with_schedule(tmp_path, capsys):
    from envault.schedule import save_schedule
    save_schedule(tmp_path, 14)
    ns = _ns(config_dir=str(tmp_path))
    cmd_schedule_show(ns)
    assert "14" in capsys.readouterr().out


def test_cmd_schedule_delete_success(tmp_path, capsys):
    from envault.schedule import save_schedule
    save_schedule(tmp_path, 3)
    ns = _ns(config_dir=str(tmp_path))
    cmd_schedule_delete(ns)
    assert "removed" in capsys.readouterr().out


def test_cmd_schedule_delete_missing_exits(tmp_path):
    ns = _ns(config_dir=str(tmp_path))
    with pytest.raises(SystemExit) as exc:
        cmd_schedule_delete(ns)
    assert exc.value.code == 1


def test_cmd_schedule_check_not_due(tmp_path, capsys):
    from envault.schedule import save_schedule
    from datetime import datetime, timedelta
    save_schedule(tmp_path, 30)
    recent = (datetime.utcnow() - timedelta(days=1)).isoformat()
    with patch("envault.cli_schedule.load_last_rotation", return_value=None):
        with patch("envault.cli_schedule.check_schedule_due", return_value=False):
            ns = _ns(config_dir=str(tmp_path))
            cmd_schedule_check(ns)
    assert "not yet due" in capsys.readouterr().out


def test_cmd_schedule_check_due_exits_2(tmp_path):
    with patch("envault.cli_schedule.load_last_rotation", return_value=None):
        with patch("envault.cli_schedule.check_schedule_due", return_value=True):
            ns = _ns(config_dir=str(tmp_path))
            with pytest.raises(SystemExit) as exc:
                cmd_schedule_check(ns)
            assert exc.value.code == 2
