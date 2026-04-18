"""Validate .env files against a required-keys schema."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


class ValidateError(Exception):
    """Raised for validation infrastructure errors."""


@dataclass
class ValidationIssue:
    key: str
    message: str

    def __str__(self) -> str:
        return f"{self.key}: {self.message}"


@dataclass
class ValidationResult:
    issues: List[ValidationIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.issues) == 0

    def summary(self) -> str:
        if self.ok:
            return "All required keys present and valid."
        lines = [str(i) for i in self.issues]
        return "\n".join(lines)


def _parse_env(text: str) -> dict:
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def validate_env(
    env_path: Path,
    required_keys: List[str],
    pattern_rules: Optional[dict] = None,
) -> ValidationResult:
    """Validate env file for required keys and optional regex patterns."""
    if not env_path.exists():
        raise ValidateError(f"Env file not found: {env_path}")

    text = env_path.read_text()
    env = _parse_env(text)
    issues: List[ValidationIssue] = []

    for key in required_keys:
        if key not in env:
            issues.append(ValidationIssue(key, "missing required key"))
        elif env[key] == "":
            issues.append(ValidationIssue(key, "value is empty"))

    if pattern_rules:
        for key, pattern in pattern_rules.items():
            if key in env and env[key] != "":
                if not re.fullmatch(pattern, env[key]):
                    issues.append(ValidationIssue(key, f"value does not match pattern '{pattern}'"))

    return ValidationResult(issues=issues)
