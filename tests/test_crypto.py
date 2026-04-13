"""Tests for envault.crypto module."""

import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from envault.crypto import encrypt_file, decrypt_file, list_keys, GPGError


@pytest.fixture
def tmp_env_file(tmp_path):
    env = tmp_path / ".env"
    env.write_text("SECRET=hunter2\nAPI_KEY=abc123\n")
    return env


def test_encrypt_file_calls_gpg(tmp_env_file, tmp_path):
    output = tmp_path / ".env.gpg"
    mock_result = MagicMock(returncode=0, stderr="")
    with patch("envault.crypto.shutil.which", return_value="/usr/bin/gpg"), \
         patch("envault.crypto.subprocess.run", return_value=mock_result) as mock_run:
        encrypt_file(tmp_env_file, output, recipient="test@example.com")
        args = mock_run.call_args[0][0]
        assert "--encrypt" in args
        assert "--recipient" in args
        assert "test@example.com" in args


def test_encrypt_file_raises_on_gpg_missing(tmp_env_file, tmp_path):
    output = tmp_path / ".env.gpg"
    with patch("envault.crypto.shutil.which", return_value=None):
        with pytest.raises(GPGError, match="gpg binary not found"):
            encrypt_file(tmp_env_file, output, recipient="test@example.com")


def test_encrypt_file_raises_on_failure(tmp_env_file, tmp_path):
    output = tmp_path / ".env.gpg"
    mock_result = MagicMock(returncode=1, stderr="No public key")
    with patch("envault.crypto.shutil.which", return_value="/usr/bin/gpg"), \
         patch("envault.crypto.subprocess.run", return_value=mock_result):
        with pytest.raises(GPGError, match="Encryption failed"):
            encrypt_file(tmp_env_file, output, recipient="test@example.com")


def test_decrypt_file_calls_gpg(tmp_path):
    enc = tmp_path / ".env.gpg"
    enc.write_bytes(b"fake encrypted content")
    output = tmp_path / ".env"
    mock_result = MagicMock(returncode=0, stderr="")
    with patch("envault.crypto.shutil.which", return_value="/usr/bin/gpg"), \
         patch("envault.crypto.subprocess.run", return_value=mock_result) as mock_run:
        decrypt_file(enc, output)
        args = mock_run.call_args[0][0]
        assert "--decrypt" in args


def test_decrypt_file_raises_on_failure(tmp_path):
    enc = tmp_path / ".env.gpg"
    enc.write_bytes(b"bad data")
    output = tmp_path / ".env"
    mock_result = MagicMock(returncode=2, stderr="decryption failed")
    with patch("envault.crypto.shutil.which", return_value="/usr/bin/gpg"), \
         patch("envault.crypto.subprocess.run", return_value=mock_result):
        with pytest.raises(GPGError, match="Decryption failed"):
            decrypt_file(enc, output)


def test_list_keys_parses_output():
    fake_output = (
        "pub:u:4096:1:ABCD1234EFGH5678:2023-01-01:::u:::scESC:\n"
        "uid:u::::2023-01-01::HASH::Alice <alice@example.com>:::::::::0:\n"
    )
    mock_result = MagicMock(returncode=0, stdout=fake_output, stderr="")
    with patch("envault.crypto.shutil.which", return_value="/usr/bin/gpg"), \
         patch("envault.crypto.subprocess.run", return_value=mock_result):
        keys = list_keys()
        assert len(keys) == 1
        assert keys[0]["uid"] == "Alice <alice@example.com>"
