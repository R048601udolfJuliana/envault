"""Tests for envault.keys module."""

from unittest.mock import MagicMock, patch

import pytest

from envault.keys import GPGKey, KeyError, _parse_colon_output, import_key, list_public_keys


# ---------------------------------------------------------------------------
# GPGKey unit tests
# ---------------------------------------------------------------------------

def test_gpgkey_short_id():
    key = GPGKey(fingerprint="AABBCCDDEEFF00112233445566778899AABBCCDD")
    assert key.short_id == "66778899AABBCCDD"


def test_gpgkey_str_with_uids():
    key = GPGKey(fingerprint="AABBCCDDEEFF00112233445566778899AABBCCDD", uids=["Alice <alice@example.com>"])
    assert "Alice" in str(key)
    assert "66778899AABBCCDD" in str(key)


def test_gpgkey_str_no_uids():
    key = GPGKey(fingerprint="AABBCCDDEEFF00112233445566778899AABBCCDD")
    assert "<no UID>" in str(key)


# ---------------------------------------------------------------------------
# _parse_colon_output
# ---------------------------------------------------------------------------

COLON_OUTPUT = """\
pub:u:4096:1:1234567890ABCDEF:2023-01-01:::u:::scESC:
fpr:::::::::AABBCCDDEEFF00112233445566778899AABBCCDD:
uid:u::::2023-01-01::HASH::Alice <alice@example.com>::::::::::0:
"""


def test_parse_colon_output_basic():
    keys = _parse_colon_output(COLON_OUTPUT, key_type="pub")
    assert len(keys) == 1
    assert keys[0].fingerprint == "AABBCCDDEEFF00112233445566778899AABBCCDD"
    assert "Alice <alice@example.com>" in keys[0].uids


def test_parse_colon_output_empty():
    assert _parse_colon_output("") == []


# ---------------------------------------------------------------------------
# list_public_keys
# ---------------------------------------------------------------------------

def test_list_public_keys_raises_when_gpg_missing():
    with patch("envault.keys._gpg_available", return_value=False):
        with pytest.raises(KeyError, match="GPG executable not found"):
            list_public_keys()


def test_list_public_keys_raises_on_failure():
    mock_result = MagicMock(returncode=1, stderr="no keys found")
    with patch("envault.keys._gpg_available", return_value=True):
        with patch("subprocess.run", return_value=mock_result):
            with pytest.raises(KeyError, match="GPG list-keys failed"):
                list_public_keys()


def test_list_public_keys_success():
    mock_result = MagicMock(returncode=0, stdout=COLON_OUTPUT)
    with patch("envault.keys._gpg_available", return_value=True):
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            keys = list_public_keys(pattern="alice")
            assert len(keys) == 1
            assert keys[0].fingerprint == "AABBCCDDEEFF00112233445566778899AABBCCDD"
            cmd_args = mock_run.call_args[0][0]
            assert "alice" in cmd_args


# ---------------------------------------------------------------------------
# import_key
# ---------------------------------------------------------------------------

def test_import_key_raises_when_gpg_missing():
    with patch("envault.keys._gpg_available", return_value=False):
        with pytest.raises(KeyError, match="GPG executable not found"):
            import_key("-----BEGIN PGP PUBLIC KEY BLOCK-----")


def test_import_key_raises_on_failure():
    mock_result = MagicMock(returncode=2, stderr="invalid key data")
    with patch("envault.keys._gpg_available", return_value=True):
        with patch("subprocess.run", return_value=mock_result):
            with pytest.raises(KeyError, match="GPG import failed"):
                import_key("bad data")


def test_import_key_success():
    mock_result = MagicMock(
        returncode=0,
        stdout="",
        stderr="gpg: key AABBCCDD1234ABCD: public key \"Bob <bob@example.com>\" imported",
    )
    with patch("envault.keys._gpg_available", return_value=True):
        with patch("subprocess.run", return_value=mock_result):
            fingerprint = import_key("-----BEGIN PGP PUBLIC KEY BLOCK-----")
            # Returns whatever fragment was parsed; just ensure no exception
            assert isinstance(fingerprint, str)
