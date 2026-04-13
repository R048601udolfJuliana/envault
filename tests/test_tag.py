"""Tests for envault.tag module."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.tag import (
    TagError,
    add_tag,
    files_for_tag,
    list_tags,
    load_tags,
    remove_tag,
    save_tags,
)


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_load_tags_missing_file_returns_empty(tmp_dir: Path) -> None:
    assert load_tags(tmp_dir) == {}


def test_save_and_load_roundtrip(tmp_dir: Path) -> None:
    data = {"release": ["prod.env.gpg"], "dev": ["dev.env.gpg"]}
    save_tags(tmp_dir, data)
    assert load_tags(tmp_dir) == data


def test_load_tags_invalid_json_raises(tmp_dir: Path) -> None:
    (tmp_dir / ".envault_tags.json").write_text("not json", encoding="utf-8")
    with pytest.raises(TagError, match="Invalid JSON"):
        load_tags(tmp_dir)


def test_load_tags_non_object_raises(tmp_dir: Path) -> None:
    (tmp_dir / ".envault_tags.json").write_text(json.dumps([1, 2, 3]), encoding="utf-8")
    with pytest.raises(TagError, match="JSON object"):
        load_tags(tmp_dir)


def test_add_tag_new(tmp_dir: Path) -> None:
    add_tag(tmp_dir, "prod", "prod.env.gpg")
    tags = load_tags(tmp_dir)
    assert tags == {"prod": ["prod.env.gpg"]}


def test_add_tag_duplicate_not_duplicated(tmp_dir: Path) -> None:
    add_tag(tmp_dir, "prod", "prod.env.gpg")
    add_tag(tmp_dir, "prod", "prod.env.gpg")
    assert load_tags(tmp_dir)["prod"] == ["prod.env.gpg"]


def test_add_tag_empty_name_raises(tmp_dir: Path) -> None:
    with pytest.raises(TagError, match="empty"):
        add_tag(tmp_dir, "  ", "file.gpg")


def test_remove_tag_success(tmp_dir: Path) -> None:
    add_tag(tmp_dir, "prod", "prod.env.gpg")
    remove_tag(tmp_dir, "prod", "prod.env.gpg")
    assert load_tags(tmp_dir) == {}


def test_remove_tag_cleans_empty_tag(tmp_dir: Path) -> None:
    add_tag(tmp_dir, "prod", "a.gpg")
    remove_tag(tmp_dir, "prod", "a.gpg")
    assert "prod" not in load_tags(tmp_dir)


def test_remove_tag_not_found_raises(tmp_dir: Path) -> None:
    with pytest.raises(TagError, match="not tagged"):
        remove_tag(tmp_dir, "missing", "file.gpg")


def test_files_for_tag_returns_list(tmp_dir: Path) -> None:
    add_tag(tmp_dir, "ci", "ci.env.gpg")
    assert files_for_tag(tmp_dir, "ci") == ["ci.env.gpg"]


def test_files_for_tag_unknown_returns_empty(tmp_dir: Path) -> None:
    assert files_for_tag(tmp_dir, "nope") == []


def test_list_tags_returns_all(tmp_dir: Path) -> None:
    add_tag(tmp_dir, "a", "x.gpg")
    add_tag(tmp_dir, "b", "y.gpg")
    result = list_tags(tmp_dir)
    assert set(result.keys()) == {"a", "b"}
