"""CLI subcommands for envault policy management."""
from __future__ import annotations

import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

from envault.policy import (
    PolicyError,
    PolicyRule,
    check_policy,
    load_policy,
    save_policy,
)


def _parse_env_file(path: Path) -> dict:
    env: dict = {}
    if not path.exists():
        return env
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def cmd_policy_add(ns: Namespace) -> None:
    config_dir = Path(ns.config_dir)
    try:
        rules = load_policy(config_dir)
    except PolicyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
    rules.append(
        PolicyRule(
            key=ns.key,
            required=not ns.optional,
            min_length=ns.min_length,
            pattern=ns.pattern,
        )
    )
    save_policy(config_dir, rules)
    print(f"Policy rule added for '{ns.key}'.")


def cmd_policy_list(ns: Namespace) -> None:
    config_dir = Path(ns.config_dir)
    try:
        rules = load_policy(config_dir)
    except PolicyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
    if not rules:
        print("No policy rules defined.")
        return
    for r in rules:
        parts = [f"key={r.key}", f"required={r.required}"]
        if r.min_length is not None:
            parts.append(f"min_length={r.min_length}")
        if r.pattern:
            parts.append(f"pattern={r.pattern}")
        print("  " + ", ".join(parts))


def cmd_policy_check(ns: Namespace) -> None:
    config_dir = Path(ns.config_dir)
    try:
        rules = load_policy(config_dir)
    except PolicyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
    env = _parse_env_file(Path(ns.env_file))
    violations = check_policy(env, rules)
    if not violations:
        print("Policy check passed.")
        return
    for v in violations:
        print(f"  FAIL  {v}")
    sys.exit(1)


def register_subcommands(sub) -> None:
    p_add = sub.add_parser("policy-add", help="Add a policy rule")
    p_add.add_argument("key")
    p_add.add_argument("--optional", action="store_true")
    p_add.add_argument("--min-length", type=int, dest="min_length")
    p_add.add_argument("--pattern")
    p_add.add_argument("--config-dir", default=".")
    p_add.set_defaults(func=cmd_policy_add)

    p_list = sub.add_parser("policy-list", help="List policy rules")
    p_list.add_argument("--config-dir", default=".")
    p_list.set_defaults(func=cmd_policy_list)

    p_check = sub.add_parser("policy-check", help="Check .env against policy")
    p_check.add_argument("--env-file", default=".env")
    p_check.add_argument("--config-dir", default=".")
    p_check.set_defaults(func=cmd_policy_check)
