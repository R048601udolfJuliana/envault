"""Tests for envault.cli_policy."""
from __future__ import annotations

import sys
import pytest
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

from envault.cli_policy import cmd_policy_add, cmd_policy_check, cmd_policy_list
from envault.policy import PolicyRule, save_policy


def _ns(**kwargs):
    defaults = {"config_dir": "", "key": "KEY", "optional": False,
                "min_length": None, "pattern": None, "env_file": ".env"}
    defaults.update(kwargs)
    return Namespace(**defaults)


def test_cmd_policy_add_success(tmp_path):
    ns = _ns(config_dir=str(tmp_path), key="DATABASE_URL", min_length=8)
    cmd_policy_add(ns)
    from envault.policy import load_policy
    rules = load_policy(tmp_path)
    assert any(r.key == "DATABASE_URL" for r in rules)


def test_cmd_policy_add_optional(tmp_path):
    ns = _ns(config_dir=str(tmp_path), key="OPTIONAL_VAR", optional=True)
    cmd_policy_add(ns)
    from envault.policy import load_policy
    rules = load_policy(tmp_path)
    assert rules[0].required is False


def test_cmd_policy_list_empty(tmp_path, capsys):
    ns = _ns(config_dir=str(tmp_path))
    cmd_policy_list(ns)
    out = capsys.readouterr().out
    assert "No policy rules" in out


def test_cmd_policy_list_with_rules(tmp_path, capsys):
    save_policy(tmp_path, [PolicyRule(key="SECRET", required=True, min_length=12)])
    ns = _ns(config_dir=str(tmp_path))
    cmd_policy_list(ns)
    out = capsys.readouterr().out
    assert "SECRET" in out
    assert "min_length=12" in out


def test_cmd_policy_check_passes(tmp_path, capsys):
    env_file = tmp_path / ".env"
    env_file.write_text('API_KEY="supersecret"\n')
    save_policy(tmp_path, [PolicyRule(key="API_KEY", required=True, min_length=5)])
    ns = _ns(config_dir=str(tmp_path), env_file=str(env_file))
    cmd_policy_check(ns)
    out = capsys.readouterr().out
    assert "passed" in out


def test_cmd_policy_check_fails_exits(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("OTHER=value\n")
    save_policy(tmp_path, [PolicyRule(key="REQUIRED_KEY", required=True)])
    ns = _ns(config_dir=str(tmp_path), env_file=str(env_file))
    with pytest.raises(SystemExit) as exc:
        cmd_policy_check(ns)
    assert exc.value.code == 1


def test_cmd_policy_add_error_exits(tmp_path):
    (tmp_path / ".envault_policy.json").write_text("bad json")
    ns = _ns(config_dir=str(tmp_path), key="X")
    with pytest.raises(SystemExit):
        cmd_policy_add(ns)
