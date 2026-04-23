"""Tests for envault.env_head and envault.cli_head."""
from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from envault.env_head import HeadError, head_env, _parse_env


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content, encoding="utf-8")
    return p


def test_parse_env_basic():
    pairs = _parse_env("FOO=bar\nBAZ=qux\n")
    assert pairs == [("FOO", "bar"), ("BAZ", "qux")]


def test_parse_env_ignores_comments_and_blanks():
    pairs = _parse_env("# comment\n\nFOO=bar\n")
    assert pairs == [("FOO", "bar")]


def test_parse_env_strips_quotes():
    pairs = _parse_env('KEY="hello world"\n')
    assert pairs == [("KEY", "hello world")]


def test_parse_env_empty_string():
    """An empty input should return an empty list without raising."""
    pairs = _parse_env("")
    assert pairs == []


def test_parse_env_value_contains_equals():
    """Values that contain '=' should be preserved correctly."""
    pairs = _parse_env("URL=http://example.com?a=1&b=2\n")
    assert pairs == [("URL", "http://example.com?a=1&b=2")]


def test_head_env_returns_first_n(tmp_dir: Path):
    f = _write(tmp_dir / ".env", "A=1\nB=2\nC=3\nD=4\n")
    result = head_env(f, n=2)
    assert result == [("A", "1"), ("B", "2")]


def test_head_env_n_larger_than_file(tmp_dir: Path):
    f = _write(tmp_dir / ".env", "A=1\nB=2\n")
    result = head_env(f, n=100)
    assert len(result) == 2


def test_head_env_missing_file_raises(tmp_dir: Path):
    with pytest.raises(HeadError, match="not found"):
        head_env(tmp_dir / "missing.env")


def test_head_env_invalid_n_raises(tmp_dir: Path):
    f = _write(tmp_dir / ".env", "A=1\n")
    with pytest.raises(HeadError, match=">= 1"):
        head_env(f, n=0)


def test_cmd_head_prints_pairs(tmp_dir: Path, capsys):
    from envault.cli_head import cmd_head

    env_file = _write(tmp_dir / ".env", "FOO=bar\nBAZ=qux\n")
    cfg = MagicMock(env_file=str(env_file))
    ns = argparse.Namespace(config="envault.json", file=None, n=1, keys_only=False)
    with patch("envault.cli_head._load_config", return_value=cfg):
        cmd_head(ns)
    out = capsys.readouterr().out
    assert "FOO=bar" in out
    assert "BAZ" not in out


def test_cmd_head_keys_only(tmp_dir: Path, capsys):
    from envault.cli_head import cmd_head

    env_file = _write(tmp_dir / ".env", "FOO=bar\n")
    cfg = MagicMock(env_file=str(env_file))
    ns = argparse.Namespace(config="envault.json", file=None, n=10, keys_only=True)
    with patch("envault.cli_head._load_config", return_value=cfg):
        cmd_head(ns)
    out = capsys.readouterr().out
    assert out.strip() == "FOO"


def test_cmd_head_error_exits(tmp_dir: Path):
    from envault.cli_head import cmd_head

    cfg = MagicMock(env_file=str(tmp_dir / "missing.env"))
    ns = argparse.Namespace(config="envault.json", file=None, n=5, keys_only=False)
    with patch("envault.cli_head._load_config", return_value=cfg):
        with pytest.raises(SystemExit):
            cmd_head(ns)
