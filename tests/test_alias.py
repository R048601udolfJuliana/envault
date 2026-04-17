"""Tests for envault.alias."""
import json
import pytest
from pathlib import Path
from envault.alias import (
    AliasError,
    add_alias,
    load_aliases,
    remove_alias,
    resolve_alias,
    save_aliases,
)


@pytest.fixture
def tmp_dir(tmp_path):
    return tmp_path


def test_load_aliases_missing_returns_empty(tmp_dir):
    assert load_aliases(tmp_dir) == {}


def test_load_aliases_invalid_json_raises(tmp_dir):
    (tmp_dir / "aliases.json").write_text("not-json")
    with pytest.raises(AliasError, match="Corrupt"):
        load_aliases(tmp_dir)


def test_load_aliases_non_object_raises(tmp_dir):
    (tmp_dir / "aliases.json").write_text(json.dumps(["a", "b"]))
    with pytest.raises(AliasError, match="JSON object"):
        load_aliases(tmp_dir)


def test_save_and_load_roundtrip(tmp_dir):
    save_aliases(tmp_dir, {"prod": "production", "dev": "development"})
    result = load_aliases(tmp_dir)
    assert result == {"prod": "production", "dev": "development"}


def test_add_alias_new(tmp_dir):
    add_alias(tmp_dir, "staging", "staging-env")
    aliases = load_aliases(tmp_dir)
    assert aliases["staging"] == "staging-env"


def test_add_alias_duplicate_raises(tmp_dir):
    add_alias(tmp_dir, "prod", "production")
    with pytest.raises(AliasError, match="already exists"):
        add_alias(tmp_dir, "prod", "other")


def test_add_alias_empty_name_raises(tmp_dir):
    with pytest.raises(AliasError, match="empty"):
        add_alias(tmp_dir, "  ", "target")


def test_remove_alias_success(tmp_dir):
    add_alias(tmp_dir, "dev", "development")
    remove_alias(tmp_dir, "dev")
    assert "dev" not in load_aliases(tmp_dir)


def test_remove_alias_not_found_raises(tmp_dir):
    with pytest.raises(AliasError, match="not found"):
        remove_alias(tmp_dir, "ghost")


def test_resolve_alias_success(tmp_dir):
    add_alias(tmp_dir, "p", "production")
    assert resolve_alias(tmp_dir, "p") == "production"


def test_resolve_alias_missing_raises(tmp_dir):
    with pytest.raises(AliasError, match="not found"):
        resolve_alias(tmp_dir, "nope")
