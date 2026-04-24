"""Tests for envault.env_protect."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.env_protect import (
    ProtectError,
    check_protected,
    is_protected,
    load_protected,
    protect_key,
    save_protected,
    unprotect_key,
)


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_load_protected_missing_file_returns_empty(tmp_dir: Path) -> None:
    assert load_protected(tmp_dir) == []


def test_save_and_load_roundtrip(tmp_dir: Path) -> None:
    save_protected(tmp_dir, ["DB_PASSWORD", "SECRET_KEY"])
    result = load_protected(tmp_dir)
    assert "DB_PASSWORD" in result
    assert "SECRET_KEY" in result


def test_load_protected_invalid_json_raises(tmp_dir: Path) -> None:
    (tmp_dir / ".envault_protected.json").write_text("not json")
    with pytest.raises(ProtectError, match="Corrupt"):
        load_protected(tmp_dir)


def test_load_protected_non_array_raises(tmp_dir: Path) -> None:
    (tmp_dir / ".envault_protected.json").write_text(json.dumps({"key": "val"}))
    with pytest.raises(ProtectError, match="JSON array"):
        load_protected(tmp_dir)


def test_protect_key_adds_key(tmp_dir: Path) -> None:
    protect_key(tmp_dir, "API_KEY")
    assert "API_KEY" in load_protected(tmp_dir)


def test_protect_key_idempotent(tmp_dir: Path) -> None:
    protect_key(tmp_dir, "API_KEY")
    protect_key(tmp_dir, "API_KEY")
    assert load_protected(tmp_dir).count("API_KEY") == 1


def test_unprotect_key_removes_key(tmp_dir: Path) -> None:
    protect_key(tmp_dir, "DB_PASS")
    unprotect_key(tmp_dir, "DB_PASS")
    assert "DB_PASS" not in load_protected(tmp_dir)


def test_unprotect_key_not_found_raises(tmp_dir: Path) -> None:
    with pytest.raises(ProtectError, match="not protected"):
        unprotect_key(tmp_dir, "MISSING_KEY")


def test_is_protected_true(tmp_dir: Path) -> None:
    protect_key(tmp_dir, "TOKEN")
    assert is_protected(tmp_dir, "TOKEN") is True


def test_is_protected_false(tmp_dir: Path) -> None:
    assert is_protected(tmp_dir, "TOKEN") is False


def test_check_protected_raises_on_blocked(tmp_dir: Path) -> None:
    protect_key(tmp_dir, "SECRET")
    with pytest.raises(ProtectError, match="SECRET"):
        check_protected(tmp_dir, ["SECRET", "OTHER"])


def test_check_protected_force_bypasses(tmp_dir: Path) -> None:
    protect_key(tmp_dir, "SECRET")
    # Should not raise
    check_protected(tmp_dir, ["SECRET"], force=True)


def test_check_protected_no_overlap_passes(tmp_dir: Path) -> None:
    protect_key(tmp_dir, "SECRET")
    check_protected(tmp_dir, ["SAFE_KEY"])
