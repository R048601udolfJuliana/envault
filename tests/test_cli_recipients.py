"""Tests for envault.cli_recipients sub-commands."""

from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import patch

import pytest

from envault.cli_recipients import (
    cmd_recipients_add,
    cmd_recipients_list,
    cmd_recipients_remove,
    register_subcommands,
)
from envault.recipients import RecipientsError


def _ns(**kwargs) -> argparse.Namespace:
    defaults = {"dir": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_recipients_add_success(tmp_path: Path, capsys) -> None:
    args = _ns(fingerprint="AABBCCDD", dir=str(tmp_path))
    rc = cmd_recipients_add(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "AABBCCDD" in out


def test_cmd_recipients_add_error(tmp_path: Path, capsys) -> None:
    args = _ns(fingerprint="AABBCCDD", dir=str(tmp_path))
    with patch("envault.cli_recipients.add_recipient", side_effect=RecipientsError("boom")):
        rc = cmd_recipients_add(args)
    assert rc == 1
    assert "boom" in capsys.readouterr().err


def test_cmd_recipients_remove_success(tmp_path: Path, capsys) -> None:
    from envault.recipients import save_recipients
    save_recipients(["AABBCCDD"], tmp_path)
    args = _ns(fingerprint="AABBCCDD", dir=str(tmp_path))
    rc = cmd_recipients_remove(args)
    assert rc == 0
    assert "AABBCCDD" in capsys.readouterr().out


def test_cmd_recipients_remove_not_found(tmp_path: Path, capsys) -> None:
    args = _ns(fingerprint="ZZZZ", dir=str(tmp_path))
    rc = cmd_recipients_remove(args)
    assert rc == 1
    assert "not found" in capsys.readouterr().err


def test_cmd_recipients_list_empty(tmp_path: Path, capsys) -> None:
    args = _ns(dir=str(tmp_path))
    rc = cmd_recipients_list(args)
    assert rc == 0
    assert "No recipients" in capsys.readouterr().out


def test_cmd_recipients_list_with_entries(tmp_path: Path, capsys) -> None:
    from envault.keys import GPGKey
    from envault.recipients import save_recipients

    save_recipients(["AAAA"], tmp_path)
    key = GPGKey(fingerprint="AAAA", key_id="AAAA", uids=["Alice <a@example.com>"])
    with patch("envault.cli_recipients.resolve_recipients", return_value=[key]):
        rc = cmd_recipients_list(_ns(dir=str(tmp_path)))
    assert rc == 0
    assert "AAAA" in capsys.readouterr().out


def test_register_subcommands_attaches_parser() -> None:
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers(dest="cmd")
    register_subcommands(subs)
    args = parser.parse_args(["recipients", "list"])
    assert args.recipients_cmd == "list"
    assert callable(args.func)
