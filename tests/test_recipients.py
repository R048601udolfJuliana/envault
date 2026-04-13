"""Tests for envault.recipients module."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from envault.recipients import (
    RECIPIENTS_FILE,
    RecipientsError,
    add_recipient,
    load_recipients,
    remove_recipient,
    resolve_recipients,
    save_recipients,
)


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_load_recipients_missing_file_returns_empty(tmp_dir: Path) -> None:
    assert load_recipients(tmp_dir) == []


def test_save_and_load_roundtrip(tmp_dir: Path) -> None:
    fps = ["AABBCCDD", "11223344"]
    save_recipients(fps, tmp_dir)
    assert load_recipients(tmp_dir) == fps


def test_load_recipients_invalid_json_raises(tmp_dir: Path) -> None:
    (tmp_dir / RECIPIENTS_FILE).write_text("not-json")
    with pytest.raises(RecipientsError, match="Failed to read"):
        load_recipients(tmp_dir)


def test_add_recipient_new(tmp_dir: Path) -> None:
    result = add_recipient("AABBCCDD", tmp_dir)
    assert result == ["AABBCCDD"]
    assert load_recipients(tmp_dir) == ["AABBCCDD"]


def test_add_recipient_duplicate_is_idempotent(tmp_dir: Path) -> None:
    add_recipient("AABBCCDD", tmp_dir)
    result = add_recipient("AABBCCDD", tmp_dir)
    assert result == ["AABBCCDD"]


def test_add_multiple_recipients(tmp_dir: Path) -> None:
    add_recipient("AAAA", tmp_dir)
    add_recipient("BBBB", tmp_dir)
    assert load_recipients(tmp_dir) == ["AAAA", "BBBB"]


def test_remove_recipient(tmp_dir: Path) -> None:
    save_recipients(["AAAA", "BBBB"], tmp_dir)
    result = remove_recipient("AAAA", tmp_dir)
    assert result == ["BBBB"]
    assert load_recipients(tmp_dir) == ["BBBB"]


def test_remove_recipient_not_found_raises(tmp_dir: Path) -> None:
    save_recipients(["AAAA"], tmp_dir)
    with pytest.raises(RecipientsError, match="not found"):
        remove_recipient("ZZZZ", tmp_dir)


def test_resolve_recipients_filters_unavailable(tmp_dir: Path) -> None:
    from envault.keys import GPGKey

    key_a = GPGKey(fingerprint="AAAA", key_id="AAAA", uids=["Alice <a@example.com>"])
    key_b = GPGKey(fingerprint="BBBB", key_id="BBBB", uids=["Bob <b@example.com>"])

    save_recipients(["AAAA", "CCCC"], tmp_dir)  # CCCC not in keyring

    with patch("envault.recipients.list_public_keys", return_value=[key_a, key_b]):
        resolved = resolve_recipients(tmp_dir)

    assert resolved == [key_a]


def test_resolve_recipients_empty(tmp_dir: Path) -> None:
    with patch("envault.recipients.list_public_keys", return_value=[]):
        assert resolve_recipients(tmp_dir) == []
