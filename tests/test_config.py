"""Tests for envault.config module."""

import json
from pathlib import Path

import pytest

from envault.config import (
    EnvaultConfig,
    ConfigError,
    load_config,
    save_config,
    CONFIG_FILENAME,
)


def test_envault_config_to_dict():
    cfg = EnvaultConfig(
        env_file=".env",
        recipients=["alice@example.com", "bob@example.com"],
    )
    d = cfg.to_dict()
    assert d["env_file"] == ".env"
    assert d["recipients"] == ["alice@example.com", "bob@example.com"]
    assert d["encrypted_file"] == ".env.gpg"


def test_envault_config_custom_encrypted_file():
    cfg = EnvaultConfig(env_file=".env", recipients=["x@y.com"], encrypted_file="secrets.gpg")
    assert cfg.encrypted_file == "secrets.gpg"


def test_from_dict_success():
    data = {"env_file": ".env", "recipients": ["a@b.com"]}
    cfg = EnvaultConfig.from_dict(data)
    assert cfg.env_file == ".env"
    assert cfg.recipients == ["a@b.com"]


def test_from_dict_missing_key_raises():
    with pytest.raises(ConfigError, match="Missing required config keys"):
        EnvaultConfig.from_dict({"env_file": ".env"})


def test_save_and_load_config(tmp_path):
    cfg = EnvaultConfig(
        env_file=".env",
        recipients=["dev@company.com"],
        encrypted_file=".env.gpg",
    )
    save_config(cfg, directory=tmp_path)
    config_path = tmp_path / CONFIG_FILENAME
    assert config_path.exists()

    loaded = load_config(directory=tmp_path)
    assert loaded.env_file == cfg.env_file
    assert loaded.recipients == cfg.recipients
    assert loaded.encrypted_file == cfg.encrypted_file


def test_load_config_missing_file_raises(tmp_path):
    with pytest.raises(ConfigError, match="No .envault.json found"):
        load_config(directory=tmp_path)


def test_load_config_invalid_json_raises(tmp_path):
    (tmp_path / CONFIG_FILENAME).write_text("not json{{{")
    with pytest.raises(ConfigError, match="Invalid JSON"):
        load_config(directory=tmp_path)


def test_save_config_writes_valid_json(tmp_path):
    cfg = EnvaultConfig(env_file=".env", recipients=["z@z.com"])
    save_config(cfg, directory=tmp_path)
    raw = (tmp_path / CONFIG_FILENAME).read_text()
    parsed = json.loads(raw)
    assert parsed["recipients"] == ["z@z.com"]
