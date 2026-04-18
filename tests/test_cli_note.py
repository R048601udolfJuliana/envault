"""Tests for envault.cli_note."""
from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import patch

import pytest

from envault.cli_note import cmd_note_add, cmd_note_clear, cmd_note_list
from envault.note import NoteError


def _ns(**kwargs) -> argparse.Namespace:
    defaults = {"config_dir": ".", "profile": "default", "text": "", "author": ""}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_note_add_success(tmp_path, capsys):
    ns = _ns(config_dir=str(tmp_path), profile="prod", text="hello", author="bob")
    cmd_note_add(ns)
    out = capsys.readouterr().out
    assert "prod" in out


def test_cmd_note_add_error_exits(capsys):
    with patch("envault.cli_note.add_note", side_effect=NoteError("bad")):
        with pytest.raises(SystemExit) as exc:
            cmd_note_add(_ns())
        assert exc.value.code == 1
    assert "bad" in capsys.readouterr().err


def test_cmd_note_list_empty(tmp_path, capsys):
    ns = _ns(config_dir=str(tmp_path), profile="")
    cmd_note_list(ns)
    assert "No notes" in capsys.readouterr().out


def test_cmd_note_list_shows_entries(tmp_path, capsys):
    from envault.note import add_note
    add_note(tmp_path, "prod", "deploy done", "alice")
    ns = _ns(config_dir=str(tmp_path), profile="")
    cmd_note_list(ns)
    out = capsys.readouterr().out
    assert "deploy done" in out
    assert "alice" in out


def test_cmd_note_list_error_exits(capsys):
    with patch("envault.cli_note.list_notes", side_effect=NoteError("oops")):
        with pytest.raises(SystemExit) as exc:
            cmd_note_list(_ns())
        assert exc.value.code == 1


def test_cmd_note_clear_success(tmp_path, capsys):
    from envault.note import add_note
    add_note(tmp_path, "prod", "old note")
    ns = _ns(config_dir=str(tmp_path), profile="")
    cmd_note_clear(ns)
    assert "1" in capsys.readouterr().out


def test_cmd_note_clear_error_exits(capsys):
    with patch("envault.cli_note.clear_notes", side_effect=NoteError("fail")):
        with pytest.raises(SystemExit) as exc:
            cmd_note_clear(_ns())
        assert exc.value.code == 1
