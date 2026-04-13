"""Tests for envault.passphrase."""

from __future__ import annotations

import pytest

import envault.passphrase as pp
from envault.passphrase import PassphraseError, get_passphrase, passphrase_from_env


# ---------------------------------------------------------------------------
# passphrase_from_env
# ---------------------------------------------------------------------------

def test_passphrase_from_env_returns_value(monkeypatch):
    monkeypatch.setenv(pp._ENV_VAR, "supersecret")
    assert passphrase_from_env() == "supersecret"


def test_passphrase_from_env_returns_none_when_unset(monkeypatch):
    monkeypatch.delenv(pp._ENV_VAR, raising=False)
    assert passphrase_from_env() is None


# ---------------------------------------------------------------------------
# _validate
# ---------------------------------------------------------------------------

def test_validate_raises_on_empty():
    with pytest.raises(PassphraseError, match="empty"):
        pp._validate("")


def test_validate_raises_when_too_short():
    with pytest.raises(PassphraseError, match="at least"):
        pp._validate("short")


def test_validate_passes_for_valid_passphrase():
    pp._validate("longenoughpassphrase")  # should not raise


# ---------------------------------------------------------------------------
# get_passphrase — via environment variable
# ---------------------------------------------------------------------------

def test_get_passphrase_uses_env_var(monkeypatch):
    monkeypatch.setenv(pp._ENV_VAR, "myvalidpass")
    result = get_passphrase()
    assert result == "myvalidpass"


def test_get_passphrase_env_var_too_short_raises(monkeypatch):
    monkeypatch.setenv(pp._ENV_VAR, "tiny")
    with pytest.raises(PassphraseError):
        get_passphrase()


# ---------------------------------------------------------------------------
# get_passphrase — interactive prompt (mocked)
# ---------------------------------------------------------------------------

def test_get_passphrase_prompts_user(monkeypatch):
    monkeypatch.delenv(pp._ENV_VAR, raising=False)
    monkeypatch.setattr("getpass.getpass", lambda prompt="": "promptedpass")
    result = get_passphrase()
    assert result == "promptedpass"


def test_get_passphrase_confirm_success(monkeypatch):
    monkeypatch.delenv(pp._ENV_VAR, raising=False)
    responses = iter(["validpassword", "validpassword"])
    monkeypatch.setattr("getpass.getpass", lambda prompt="": next(responses))
    result = get_passphrase(confirm=True)
    assert result == "validpassword"


def test_get_passphrase_confirm_mismatch_raises(monkeypatch):
    monkeypatch.delenv(pp._ENV_VAR, raising=False)
    responses = iter(["validpassword", "differentpass"])
    monkeypatch.setattr("getpass.getpass", lambda prompt="": next(responses))
    with pytest.raises(PassphraseError, match="do not match"):
        get_passphrase(confirm=True)
