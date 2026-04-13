"""Tests for envault.profile."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.profile import (
    ProfileError,
    add_profile,
    get_profile,
    list_profile_names,
    load_profiles,
    remove_profile,
    save_profiles,
)


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_load_profiles_missing_file_returns_empty(tmp_dir):
    assert load_profiles(tmp_dir) == {}


def test_load_profiles_invalid_json_raises(tmp_dir):
    (tmp_dir / ".envault_profiles.json").write_text("not json", encoding="utf-8")
    with pytest.raises(ProfileError, match="Invalid profiles file"):
        load_profiles(tmp_dir)


def test_load_profiles_non_object_raises(tmp_dir):
    (tmp_dir / ".envault_profiles.json").write_text("[1, 2, 3]", encoding="utf-8")
    with pytest.raises(ProfileError, match="JSON object"):
        load_profiles(tmp_dir)


def test_save_and_load_roundtrip(tmp_dir):
    profiles = {"prod": {"env_file": ".env.prod", "encrypted_file": ".env.prod.gpg", "recipients_file": ".envault_recipients.json"}}
    save_profiles(tmp_dir, profiles)
    assert load_profiles(tmp_dir) == profiles


def test_add_profile_creates_entry(tmp_dir):
    result = add_profile(tmp_dir, "staging", ".env.staging")
    assert "staging" in result
    assert result["staging"]["env_file"] == ".env.staging"
    assert result["staging"]["encrypted_file"] == ".env.staging.gpg"


def test_add_profile_custom_encrypted_file(tmp_dir):
    add_profile(tmp_dir, "dev", ".env", encrypted_file="secrets.gpg")
    profile = get_profile(tmp_dir, "dev")
    assert profile["encrypted_file"] == "secrets.gpg"


def test_add_profile_persists_to_disk(tmp_dir):
    add_profile(tmp_dir, "ci", ".env.ci")
    raw = json.loads((tmp_dir / ".envault_profiles.json").read_text())
    assert "ci" in raw


def test_add_profile_empty_name_raises(tmp_dir):
    with pytest.raises(ProfileError, match="must not be empty"):
        add_profile(tmp_dir, "", ".env")


def test_remove_profile_success(tmp_dir):
    add_profile(tmp_dir, "old", ".env.old")
    remaining = remove_profile(tmp_dir, "old")
    assert "old" not in remaining


def test_remove_profile_not_found_raises(tmp_dir):
    with pytest.raises(ProfileError, match="not found"):
        remove_profile(tmp_dir, "ghost")


def test_get_profile_not_found_raises(tmp_dir):
    with pytest.raises(ProfileError, match="not found"):
        get_profile(tmp_dir, "missing")


def test_list_profile_names_sorted(tmp_dir):
    add_profile(tmp_dir, "zebra", ".env.z")
    add_profile(tmp_dir, "alpha", ".env.a")
    add_profile(tmp_dir, "beta", ".env.b")
    assert list_profile_names(tmp_dir) == ["alpha", "beta", "zebra"]


def test_list_profile_names_empty(tmp_dir):
    assert list_profile_names(tmp_dir) == []
