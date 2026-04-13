"""Tests for envault.rotate."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from envault.config import EnvaultConfig
from envault.rotate import rotate, RotationError


@pytest.fixture()
def config(tmp_path: Path) -> EnvaultConfig:
    cfg = EnvaultConfig(
        recipients=["AABBCCDD"],
        env_file=str(tmp_path / ".env"),
        encrypted_file=str(tmp_path / ".env.gpg"),
    )
    # Create a fake encrypted file so rotate() can find it.
    Path(cfg.encrypted_file).write_bytes(b"fake-gpg-data")
    return cfg


def _patch_crypto(decrypt_ok: bool = True, encrypt_ok: bool = True):
    """Return a context-manager pair that stubs crypto calls."""

    def _decrypt(src, dst, **_kwargs):
        dst.write_text("SECRET=hello")

    def _encrypt(src, dst, **_kwargs):
        dst.write_bytes(b"new-gpg-data")

    from envault.crypto import GPGError

    def _decrypt_fail(src, dst, **_kwargs):
        raise GPGError("gpg error")

    def _encrypt_fail(src, dst, **_kwargs):
        raise GPGError("gpg error")

    return (
        patch("envault.rotate.decrypt_file", side_effect=_decrypt if decrypt_ok else _decrypt_fail),
        patch("envault.rotate.encrypt_file", side_effect=_encrypt if encrypt_ok else _encrypt_fail),
    )


def test_rotate_success(config: EnvaultConfig, tmp_path: Path):
    dec_patch, enc_patch = _patch_crypto()
    with dec_patch, enc_patch:
        result = rotate(config, new_recipients=["NEWKEY01"])
    assert result == Path(config.encrypted_file)
    # Backup should have been created
    assert (tmp_path / ".env.bak.gpg").exists()


def test_rotate_dry_run_does_not_overwrite(config: EnvaultConfig, tmp_path: Path):
    original_bytes = Path(config.encrypted_file).read_bytes()
    dec_patch, enc_patch = _patch_crypto()
    with dec_patch, enc_patch:
        rotate(config, new_recipients=["NEWKEY01"], dry_run=True)
    assert Path(config.encrypted_file).read_bytes() == original_bytes
    assert not (tmp_path / ".env.bak.gpg").exists()


def test_rotate_raises_when_encrypted_file_missing(tmp_path: Path):
    cfg = EnvaultConfig(
        recipients=["AABBCCDD"],
        env_file=str(tmp_path / ".env"),
        encrypted_file=str(tmp_path / "nonexistent.gpg"),
    )
    with pytest.raises(RotationError, match="Encrypted file not found"):
        rotate(cfg, new_recipients=["NEWKEY01"])


def test_rotate_raises_on_empty_recipients(config: EnvaultConfig):
    with pytest.raises(RotationError, match="must not be empty"):
        rotate(config, new_recipients=[])


def test_rotate_raises_on_decrypt_failure(config: EnvaultConfig):
    dec_patch, enc_patch = _patch_crypto(decrypt_ok=False)
    with dec_patch, enc_patch:
        with pytest.raises(RotationError, match="Decryption failed"):
            rotate(config, new_recipients=["NEWKEY01"])


def test_rotate_raises_on_encrypt_failure(config: EnvaultConfig):
    dec_patch, enc_patch = _patch_crypto(encrypt_ok=False)
    with dec_patch, enc_patch:
        with pytest.raises(RotationError, match="Re-encryption failed"):
            rotate(config, new_recipients=["NEWKEY01"])


def test_rotate_records_audit_event(config: EnvaultConfig):
    mock_log = MagicMock()
    dec_patch, enc_patch = _patch_crypto()
    with dec_patch, enc_patch:
        rotate(config, new_recipients=["NEWKEY01"], audit_log=mock_log)
    mock_log.record.assert_called_once()
    call_kwargs = mock_log.record.call_args
    assert call_kwargs.kwargs["action"] == "rotate" or call_kwargs.args[0] == "rotate"
