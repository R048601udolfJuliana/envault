"""Tests for envault.env_defaults."""

from __future__ import annotations

from pathlib import Path

import pytest

from envault.env_defaults import DefaultsError, apply_defaults


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, text: str) -> Path:
    p.write_text(text, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# apply_defaults
# ---------------------------------------------------------------------------

def test_apply_defaults_appends_missing_key(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "FOO=bar\n")
    _, applied = apply_defaults(src, {"BAZ": "qux"})
    assert "BAZ" in applied
    assert "BAZ=qux" in src.read_text()


def test_apply_defaults_does_not_overwrite_existing(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "FOO=bar\n")
    _, applied = apply_defaults(src, {"FOO": "NEW"})
    assert "FOO" not in applied
    assert "FOO=bar" in src.read_text()


def test_apply_defaults_overwrites_empty_value_by_default(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "FOO=\n")
    _, applied = apply_defaults(src, {"FOO": "filled"})
    assert "FOO" in applied


def test_apply_defaults_no_overwrite_empty_flag(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "FOO=\n")
    _, applied = apply_defaults(src, {"FOO": "filled"}, overwrite_empty=False)
    assert "FOO" not in applied


def test_apply_defaults_writes_to_dest(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "FOO=bar\n")
    dest = tmp_dir / "out.env"
    out_path, _ = apply_defaults(src, {"NEW": "val"}, dest=dest)
    assert out_path == dest.resolve()
    assert dest.exists()
    assert "NEW=val" in dest.read_text()


def test_apply_defaults_source_unchanged_when_dest_specified(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "FOO=bar\n")
    dest = tmp_dir / "out.env"
    apply_defaults(src, {"NEW": "val"}, dest=dest)
    assert "NEW" not in src.read_text()


def test_apply_defaults_missing_source_raises(tmp_dir: Path) -> None:
    with pytest.raises(DefaultsError, match="not found"):
        apply_defaults(tmp_dir / "missing.env", {"KEY": "val"})


def test_apply_defaults_empty_defaults_raises(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "FOO=bar\n")
    with pytest.raises(DefaultsError, match="No defaults"):
        apply_defaults(src, {})


def test_apply_defaults_multiple_keys(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "A=1\n")
    _, applied = apply_defaults(src, {"B": "2", "C": "3"})
    text = src.read_text()
    assert "B=2" in text
    assert "C=3" in text
    assert set(applied) == {"B", "C"}


def test_apply_defaults_preserves_comments(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "# header\nFOO=bar\n")
    apply_defaults(src, {"NEW": "val"})
    assert "# header" in src.read_text()
