"""Tests for envault.compare and envault.cli_compare."""
from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from envault.compare import (
    _parse_env,
    compare_encrypted,
    CompareError,
    CompareResult,
)


# ---------------------------------------------------------------------------
# _parse_env
# ---------------------------------------------------------------------------

def test_parse_env_basic():
    text = 'FOO=bar\nBAZ=qux\n'
    assert _parse_env(text) == {"FOO": "bar", "BAZ": "qux"}


def test_parse_env_strips_quotes():
    text = 'KEY="hello world"\n'
    assert _parse_env(text) == {"KEY": "hello world"}


def test_parse_env_ignores_comments_and_blanks():
    text = '# comment\n\nFOO=1\n'
    assert _parse_env(text) == {"FOO": "1"}


# ---------------------------------------------------------------------------
# CompareResult
# ---------------------------------------------------------------------------

def test_compare_result_no_differences():
    r = CompareResult()
    assert not r.has_differences
    assert r.summary_lines() == []


def test_compare_result_summary_lines():
    r = CompareResult(
        only_in_a=["OLD_KEY"],
        only_in_b=["NEW_KEY"],
        changed=[("DB_URL", "sqlite", "postgres")],
    )
    lines = r.summary_lines()
    assert any("OLD_KEY" in l and "only in A" in l for l in lines)
    assert any("NEW_KEY" in l and "only in B" in l for l in lines)
    assert any("DB_URL" in l and "sqlite" in l and "postgres" in l for l in lines)


# ---------------------------------------------------------------------------
# compare_encrypted
# ---------------------------------------------------------------------------

def _make_decrypt_side_effect(contents: dict):
    """Return a side_effect that writes preset content to the output path."""
    call_count = [0]

    def _side_effect(src, dst, passphrase=None):
        key = call_count[0]
        call_count[0] += 1
        dst.write_text(list(contents.values())[key])

    return _side_effect


def test_compare_encrypted_no_diff(tmp_path):
    a = tmp_path / "a.env.gpg"
    b = tmp_path / "b.env.gpg"
    a.write_text("")
    b.write_text("")
    content = "FOO=bar\nBAZ=qux\n"
    with patch("envault.compare.decrypt_file", side_effect=_make_decrypt_side_effect({"a": content, "b": content})):
        result = compare_encrypted(a, b)
    assert not result.has_differences


def test_compare_encrypted_detects_changes(tmp_path):
    a = tmp_path / "a.env.gpg"
    b = tmp_path / "b.env.gpg"
    a.write_text("")
    b.write_text("")
    with patch(
        "envault.compare.decrypt_file",
        side_effect=_make_decrypt_side_effect({
            "a": "FOO=old\nONLY_A=1\n",
            "b": "FOO=new\nONLY_B=2\n",
        }),
    ):
        result = compare_encrypted(a, b)
    assert result.has_differences
    assert "ONLY_A" in result.only_in_a
    assert "ONLY_B" in result.only_in_b
    assert any(k == "FOO" for k, _, _ in result.changed)


def test_compare_encrypted_missing_file_raises(tmp_path):
    a = tmp_path / "a.env.gpg"
    b = tmp_path / "b.env.gpg"  # does not exist
    a.write_text("")
    with pytest.raises(CompareError, match="File B not found"):
        compare_encrypted(a, b)


def test_compare_encrypted_gpg_error_raises(tmp_path):
    from envault.crypto import GPGError
    a = tmp_path / "a.env.gpg"
    b = tmp_path / "b.env.gpg"
    a.write_text("")
    b.write_text("")
    with patch("envault.compare.decrypt_file", side_effect=GPGError("bad")):
        with pytest.raises(CompareError, match="Decryption failed"):
            compare_encrypted(a, b)


# ---------------------------------------------------------------------------
# cli_compare
# ---------------------------------------------------------------------------

def _ns(**kwargs):
    defaults = {"file_a": "a.gpg", "file_b": "b.gpg", "exit_code": False}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_compare_no_differences(capsys, tmp_path):
    from envault.cli_compare import cmd_compare
    with patch("envault.cli_compare.compare_encrypted") as mock_cmp, \
         patch("envault.cli_compare.passphrase_from_env", return_value=None):
        mock_cmp.return_value = CompareResult()
        a = tmp_path / "a.gpg"
        b = tmp_path / "b.gpg"
        cmd_compare(_ns(file_a=str(a), file_b=str(b)))
    out = capsys.readouterr().out
    assert "No differences" in out


def test_cmd_compare_with_differences_exit_code(tmp_path):
    from envault.cli_compare import cmd_compare
    result = CompareResult(only_in_a=["OLD"], only_in_b=[], changed=[])
    with patch("envault.cli_compare.compare_encrypted", return_value=result), \
         patch("envault.cli_compare.passphrase_from_env", return_value=None):
        a = tmp_path / "a.gpg"
        b = tmp_path / "b.gpg"
        with pytest.raises(SystemExit) as exc_info:
            cmd_compare(_ns(file_a=str(a), file_b=str(b), exit_code=True))
    assert exc_info.value.code == 1


def test_cmd_compare_error_exits(tmp_path, capsys):
    from envault.cli_compare import cmd_compare
    with patch("envault.cli_compare.compare_encrypted", side_effect=CompareError("boom")), \
         patch("envault.cli_compare.passphrase_from_env", return_value=None):
        a = tmp_path / "a.gpg"
        b = tmp_path / "b.gpg"
        with pytest.raises(SystemExit) as exc_info:
            cmd_compare(_ns(file_a=str(a), file_b=str(b)))
    assert exc_info.value.code == 1
    assert "boom" in capsys.readouterr().err
