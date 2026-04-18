"""Tests for envault.policy."""
from __future__ import annotations

import json
import pytest
from pathlib import Path

from envault.policy import (
    PolicyError,
    PolicyRule,
    PolicyViolation,
    check_policy,
    load_policy,
    save_policy,
)


@pytest.fixture
def tmp_dir(tmp_path):
    return tmp_path


def test_load_policy_missing_returns_empty(tmp_dir):
    assert load_policy(tmp_dir) == []


def test_save_and_load_roundtrip(tmp_dir):
    rules = [
        PolicyRule(key="DATABASE_URL", required=True, min_length=10),
        PolicyRule(key="SECRET_KEY", required=True, pattern=r"[A-Z]"),
    ]
    save_policy(tmp_dir, rules)
    loaded = load_policy(tmp_dir)
    assert len(loaded) == 2
    assert loaded[0].key == "DATABASE_URL"
    assert loaded[0].min_length == 10
    assert loaded[1].pattern == r"[A-Z]"


def test_load_policy_invalid_json_raises(tmp_dir):
    (tmp_dir / ".envault_policy.json").write_text("not json")
    with pytest.raises(PolicyError, match="Invalid policy JSON"):
        load_policy(tmp_dir)


def test_load_policy_non_array_raises(tmp_dir):
    (tmp_dir / ".envault_policy.json").write_text(json.dumps({"key": "X"}))
    with pytest.raises(PolicyError, match="JSON array"):
        load_policy(tmp_dir)


def test_check_policy_no_violations():
    rules = [PolicyRule(key="API_KEY", required=True, min_length=4)]
    violations = check_policy({"API_KEY": "abcde"}, rules)
    assert violations == []


def test_check_policy_missing_required():
    rules = [PolicyRule(key="API_KEY", required=True)]
    violations = check_policy({}, rules)
    assert len(violations) == 1
    assert "missing" in violations[0].reason


def test_check_policy_optional_missing_ok():
    rules = [PolicyRule(key="OPTIONAL_KEY", required=False)]
    violations = check_policy({}, rules)
    assert violations == []


def test_check_policy_min_length_violation():
    rules = [PolicyRule(key="TOKEN", required=True, min_length=10)]
    violations = check_policy({"TOKEN": "short"}, rules)
    assert len(violations) == 1
    assert "too short" in violations[0].reason


def test_check_policy_pattern_violation():
    rules = [PolicyRule(key="CODE", required=True, pattern=r"^\d{4}$")]
    violations = check_policy({"CODE": "abc"}, rules)
    assert len(violations) == 1
    assert "pattern" in violations[0].reason


def test_check_policy_pattern_passes():
    rules = [PolicyRule(key="CODE", required=True, pattern=r"^\d{4}$")]
    violations = check_policy({"CODE": "1234"}, rules)
    assert violations == []


def test_policy_violation_str():
    v = PolicyViolation(key="FOO", reason="required key is missing")
    assert str(v) == "FOO: required key is missing"
