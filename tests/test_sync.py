"""Tests for envault.sync push/pull operations."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from envault.sync import push, pull, SyncError
from envault.config import EnvaultConfig


@pytest.fixture
def config(tmp_path):
    return EnvaultConfig(
        recipients=["alice@example.com"],
        sync_path=str(tmp_path / "shared"),
        encrypted_file=str(tmp_path / ".env.gpg"),
    )


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("SECRET=hello\n")
    return str(p)


def test_push_calls_encrypt_and_copies(config, env_file, tmp_path):
    with patch("envault.sync.encrypt_file") as mock_enc:
        dest = push(config, env_file=env_file, force=True)
        mock_enc.assert_called_once_with(env_file, config.encrypted_file, config.recipients)
        assert Path(dest).parent == Path(config.sync_path)


def test_push_raises_when_env_missing(config, tmp_path):
    with pytest.raises(SyncError, match="Source file not found"):
        push(config, env_file=str(tmp_path / "nonexistent.env"))


def test_push_raises_on_existing_dest_without_force(config, env_file, tmp_path):
    shared = Path(config.sync_path)
    shared.mkdir(parents=True, exist_ok=True)
    dest_file = shared / Path(config.encrypted_file).name
    dest_file.write_bytes(b"existing")

    with patch("envault.sync.encrypt_file"):
        # Also need the local encrypted file to exist for shutil.copy2
        Path(config.encrypted_file).write_bytes(b"encrypted")
        with pytest.raises(SyncError, match="already exists"):
            push(config, env_file=env_file, force=False)


def test_push_raises_on_gpg_error(config, env_file):
    from envault.crypto import GPGError
    with patch("envault.sync.encrypt_file", side_effect=GPGError("gpg missing")):
        with pytest.raises(SyncError, match="Encryption failed"):
            push(config, env_file=env_file)


def test_pull_calls_decrypt_and_writes(config, tmp_path):
    shared = Path(config.sync_path)
    shared.mkdir(parents=True, exist_ok=True)
    enc_name = Path(config.encrypted_file).name
    (shared / enc_name).write_bytes(b"encrypted-data")

    output_env = str(tmp_path / ".env.out")

    with patch("envault.sync.decrypt_file") as mock_dec:
        result = pull(config, env_file=output_env, force=True)
        mock_dec.assert_called_once_with(config.encrypted_file, output_env)
        assert result == output_env


def test_pull_raises_when_source_missing(config, tmp_path):
    with pytest.raises(SyncError, match="No encrypted file found"):
        pull(config, env_file=str(tmp_path / ".env"))


def test_pull_raises_on_gpg_error(config, tmp_path):
    from envault.crypto import GPGError
    shared = Path(config.sync_path)
    shared.mkdir(parents=True, exist_ok=True)
    (shared / Path(config.encrypted_file).name).write_bytes(b"data")

    output_env = str(tmp_path / ".env.out")
    with patch("envault.sync.decrypt_file", side_effect=GPGError("bad key")):
        with pytest.raises(SyncError, match="Decryption failed"):
            pull(config, env_file=output_env, force=True)
