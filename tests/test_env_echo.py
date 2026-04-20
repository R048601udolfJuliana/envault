"""Tests for envault/env_echo.py."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.env_echo import EchoError, echo_env


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content, encoding="utf-8")
    return p


def test_echo_plain_basic(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "FOO=bar\nBAZ=qux\n")
    lines = echo_env(f, fmt="plain")
    assert lines == ["FOO=bar", "BAZ=qux"]


def test_echo_plain_strips_quotes(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", 'KEY="hello world"\n')
    lines = echo_env(f, fmt="plain")
    assert lines == ["KEY=hello world"]


def test_echo_export_format(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "A=1\nB=2\n")
    lines = echo_env(f, fmt="export")
    assert lines == ["export A=1", "export B=2"]


def test_echo_json_format(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "X=10\nY=20\n")
    lines = echo_env(f, fmt="json")
    assert len(lines) == 1
    data = json.loads(lines[0])
    assert data == {"X": "10", "Y": "20"}


def test_echo_filter_keys(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "FOO=1\nBAR=2\nBAZ=3\n")
    lines = echo_env(f, fmt="plain", keys=["FOO", "BAZ"])
    assert lines == ["FOO=1", "BAZ=3"]


def test_echo_mask(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "SECRET=topsecret\nOTHER=value\n")
    lines = echo_env(f, fmt="plain", mask=True)
    assert all(v == "***" for line in lines for k, _, v in [line.partition("=")])


def test_echo_ignores_comments_and_blanks(tmp_dir: Path) -> None:
    content = "# comment\n\nFOO=bar\n"
    f = _write(tmp_dir / ".env", content)
    lines = echo_env(f, fmt="plain")
    assert lines == ["FOO=bar"]


def test_echo_missing_file_raises(tmp_dir: Path) -> None:
    with pytest.raises(EchoError, match="not found"):
        echo_env(tmp_dir / "missing.env")


def test_echo_unknown_format_raises(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "A=1\n")
    with pytest.raises(EchoError, match="unknown format"):
        echo_env(f, fmt="yaml")  # type: ignore[arg-type]


def test_echo_filter_keys_none_match(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "FOO=1\n")
    lines = echo_env(f, fmt="plain", keys=["DOES_NOT_EXIST"])
    assert lines == []
