"""Tests for envault.cli_tag module."""
from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import patch

import pytest

from envault.cli_tag import cmd_tag_add, cmd_tag_list, cmd_tag_remove
from envault.tag import TagError


def _ns(**kwargs) -> argparse.Namespace:  # type: ignore[return]
    defaults = {"directory": ".", "tag": None, "file": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_tag_add_success(tmp_path: Path, capsys) -> None:
    ns = _ns(directory=str(tmp_path), tag="prod", file="prod.env.gpg")
    cmd_tag_add(ns)
    captured = capsys.readouterr()
    assert "Tagged" in captured.out


def test_cmd_tag_add_error_exits(capsys) -> None:
    with patch("envault.cli_tag.add_tag", side_effect=TagError("bad tag")):
        with pytest.raises(SystemExit) as exc_info:
            cmd_tag_add(_ns(directory=".", tag="", file="f.gpg"))
        assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "error" in captured.err


def test_cmd_tag_remove_success(tmp_path: Path, capsys) -> None:
    from envault.tag import add_tag
    add_tag(tmp_path, "prod", "prod.env.gpg")
    ns = _ns(directory=str(tmp_path), tag="prod", file="prod.env.gpg")
    cmd_tag_remove(ns)
    captured = capsys.readouterr()
    assert "Removed" in captured.out


def test_cmd_tag_remove_not_found_exits(capsys) -> None:
    with patch("envault.cli_tag.remove_tag", side_effect=TagError("not tagged")):
        with pytest.raises(SystemExit) as exc_info:
            cmd_tag_remove(_ns(directory=".", tag="x", file="f.gpg"))
        assert exc_info.value.code == 1


def test_cmd_tag_list_all(tmp_path: Path, capsys) -> None:
    from envault.tag import add_tag
    add_tag(tmp_path, "alpha", "a.gpg")
    add_tag(tmp_path, "beta", "b.gpg")
    ns = _ns(directory=str(tmp_path), tag=None)
    cmd_tag_list(ns)
    captured = capsys.readouterr()
    assert "alpha" in captured.out
    assert "beta" in captured.out


def test_cmd_tag_list_specific_tag(tmp_path: Path, capsys) -> None:
    from envault.tag import add_tag
    add_tag(tmp_path, "ci", "ci.gpg")
    ns = _ns(directory=str(tmp_path), tag="ci")
    cmd_tag_list(ns)
    captured = capsys.readouterr()
    assert "ci.gpg" in captured.out


def test_cmd_tag_list_empty(tmp_path: Path, capsys) -> None:
    ns = _ns(directory=str(tmp_path), tag=None)
    cmd_tag_list(ns)
    captured = capsys.readouterr()
    assert "No tags" in captured.out
