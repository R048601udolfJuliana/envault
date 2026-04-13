"""Tests for envault.verify."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.config import EnvaultConfig
from envault.verify import VerifyError, _sha256, verify_manifest, write_manifest


@pytest.fixture()
def config(tmp_path: Path) -> EnvaultConfig:
    return EnvaultConfig(
        env_file=str(tmp_path / ".env"),
        encrypted_file=str(tmp_path / ".env.gpg"),
        recipients=["alice@example.com"],
    )


@pytest.fixture()
def enc_file(config: EnvaultConfig) -> Path:
    p = Path(config.encrypted_file)
    p.write_bytes(b"encrypted-content-stub")
    return p


def test_sha256_returns_hex_string(enc_file: Path) -> None:
    digest = _sha256(enc_file)
    assert len(digest) == 64
    assert all(c in "0123456789abcdef" for c in digest)


def test_write_manifest_creates_file(config: EnvaultConfig, enc_file: Path) -> None:
    manifest_path = write_manifest(config)
    assert manifest_path.exists()
    data = json.loads(manifest_path.read_text())
    assert "sha256" in data
    assert data["file"] == enc_file.name


def test_write_manifest_missing_encrypted_file(config: EnvaultConfig) -> None:
    with pytest.raises(VerifyError, match="Encrypted file not found"):
        write_manifest(config)


def test_verify_manifest_success(config: EnvaultConfig, enc_file: Path) -> None:
    write_manifest(config)
    assert verify_manifest(config) is True


def test_verify_manifest_missing_manifest(config: EnvaultConfig, enc_file: Path) -> None:
    with pytest.raises(VerifyError, match="Manifest not found"):
        verify_manifest(config)


def test_verify_manifest_digest_mismatch(config: EnvaultConfig, enc_file: Path) -> None:
    write_manifest(config)
    # Tamper with the encrypted file after writing the manifest
    enc_file.write_bytes(b"tampered-content")
    with pytest.raises(VerifyError, match="Digest mismatch"):
        verify_manifest(config)


def test_verify_manifest_missing_encrypted_file_after_write(
    config: EnvaultConfig, enc_file: Path
) -> None:
    write_manifest(config)
    enc_file.unlink()
    with pytest.raises(VerifyError, match="Encrypted file not found"):
        verify_manifest(config)
