"""Policy enforcement for envault — define and check rules on .env files."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


class PolicyError(Exception):
    pass


@dataclass
class PolicyRule:
    key: str
    required: bool = True
    min_length: Optional[int] = None
    pattern: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "required": self.required,
            "min_length": self.min_length,
            "pattern": self.pattern,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "PolicyRule":
        return cls(
            key=d["key"],
            required=d.get("required", True),
            min_length=d.get("min_length"),
            pattern=d.get("pattern"),
        )


@dataclass
class PolicyViolation:
    key: str
    reason: str

    def __str__(self) -> str:
        return f"{self.key}: {self.reason}"


def _policy_path(config_dir: Path) -> Path:
    return config_dir / ".envault_policy.json"


def load_policy(config_dir: Path) -> List[PolicyRule]:
    path = _policy_path(config_dir)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise PolicyError(f"Invalid policy JSON: {exc}") from exc
    if not isinstance(data, list):
        raise PolicyError("Policy file must contain a JSON array.")
    return [PolicyRule.from_dict(r) for r in data]


def save_policy(config_dir: Path, rules: List[PolicyRule]) -> None:
    path = _policy_path(config_dir)
    path.write_text(json.dumps([r.to_dict() for r in rules], indent=2))


def check_policy(
    env: dict, rules: List[PolicyRule]
) -> List[PolicyViolation]:
    import re

    violations: List[PolicyViolation] = []
    for rule in rules:
        value = env.get(rule.key)
        if rule.required and value is None:
            violations.append(PolicyViolation(rule.key, "required key is missing"))
            continue
        if value is None:
            continue
        if rule.min_length is not None and len(value) < rule.min_length:
            violations.append(
                PolicyViolation(rule.key, f"value too short (min {rule.min_length})")
            )
        if rule.pattern and not re.search(rule.pattern, value):
            violations.append(
                PolicyViolation(rule.key, f"value does not match pattern '{rule.pattern}'")
            )
    return violations
