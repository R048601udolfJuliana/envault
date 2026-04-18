"""Tests for envault.sign."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from envault.sign import SignError, sign_file, verify_signature


@pytest.fixture()
def enc_file(tmp_path: Path) -> Path:
    f = tmp_path / "vault.env.gpg"
    f.write_bytes(b"encrypted")
    return f


def _ok(stderr: str = "") -> MagicMock:
    m = MagicMock()
    m.returncode = 0
    m.stderr = stderr
    return m


def _fail(stderr: str = "gpg: error") -> MagicMock:
    m = MagicMock()
    m.returncode = 1
    m.stderr = stderr
    return m


def test_sign_file_calls_gpg(enc_file: Path) -> None:
    with patch("subprocess.run", return_value=_ok()) as mock_run:
        sig = sign_file(enc_file, "ABCD1234")
        assert sig == enc_file.with_suffix(".gpg.sig")
        args = mock_run.call_args[0][0]
        assert "gpg" in args
        assert "--detach-sign" in args
        assert "ABCD1234" in args


def test_sign_file_custom_sig_path(enc_file: Path, tmp_path: Path) -> None:
    custom_sig = tmp_path / "custom.sig"
    with patch("subprocess.run", return_value=_ok()):
        result = sign_file(enc_file, "ABCD1234", sig_path=custom_sig)
    assert result == custom_sig


def test_sign_file_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(SignError, match="File not found"):
        sign_file(tmp_path / "missing.gpg", "ABCD1234")


def test_sign_file_gpg_failure_raises(enc_file: Path) -> None:
    with patch("subprocess.run", return_value=_fail("bad key")):
        with pytest.raises(SignError, match="bad key"):
            sign_file(enc_file, "BADKEY")


def test_verify_signature_success(enc_file: Path) -> None:
    sig_file = enc_file.with_suffix(".gpg.sig")
    sig_file.write_bytes(b"sig")
    stderr = "gpg: Good signature\ngpg: using key ID DEADBEEF"
    with patch("subprocess.run", return_value=_ok(stderr)):
        signer = verify_signature(enc_file)
    assert isinstance(signer, str)


def test_verify_signature_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(SignError, match="File not found"):
        verify_signature(tmp_path / "missing.gpg")


def test_verify_signature_missing_sig_raises(enc_file: Path) -> None:
    with pytest.raises(SignError, match="Signature file not found"):
        verify_signature(enc_file)


def test_verify_signature_failure_raises(enc_file: Path) -> None:
    sig_file = enc_file.with_suffix(".gpg.sig")
    sig_file.write_bytes(b"badsig")
    with patch("subprocess.run", return_value=_fail("BAD signature")):
        with pytest.raises(SignError, match="BAD signature"):
            verify_signature(enc_file)
