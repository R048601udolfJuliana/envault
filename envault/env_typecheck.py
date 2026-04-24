"""Type-checking for .env values against a schema."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


class TypeCheckError(Exception):
    """Raised on unrecoverable type-check errors."""


# Supported type names
_TYPES = {"str", "int", "float", "bool", "url", "email"}

_BOOL_TRUE = {"true", "1", "yes", "on"}
_BOOL_FALSE = {"false", "0", "no", "off"}
_URL_RE = re.compile(r"^https?://", re.IGNORECASE)
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass
class TypeIssue:
    key: str
    value: str
    expected_type: str
    message: str

    def __str__(self) -> str:
        return f"{self.key}={self.value!r} — expected {self.expected_type}: {self.message}"


@dataclass
class TypeCheckResult:
    issues: List[TypeIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.issues) == 0

    def summary_lines(self) -> List[str]:
        if self.ok:
            return ["All values match their declared types."]
        return [str(i) for i in self.issues]


def _strip_quotes(v: str) -> str:
    for q in ('"', "'"):
        if v.startswith(q) and v.endswith(q) and len(v) >= 2:
            return v[1:-1]
    return v


def _parse_env(text: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        result[key.strip()] = _strip_quotes(val.strip())
    return result


def _check_value(value: str, type_name: str) -> Optional[str]:
    """Return an error message or None if the value is valid."""
    if type_name == "int":
        try:
            int(value)
        except ValueError:
            return f"cannot parse as integer"
    elif type_name == "float":
        try:
            float(value)
        except ValueError:
            return f"cannot parse as float"
    elif type_name == "bool":
        if value.lower() not in _BOOL_TRUE | _BOOL_FALSE:
            return f"expected one of true/false/1/0/yes/no/on/off"
    elif type_name == "url":
        if not _URL_RE.match(value):
            return f"must start with http:// or https://"
    elif type_name == "email":
        if not _EMAIL_RE.match(value):
            return f"not a valid email address"
    return None


def typecheck_env(
    env_file: Path,
    schema: Dict[str, str],
) -> TypeCheckResult:
    """Check values in *env_file* against *schema* (key -> type_name)."""
    if not env_file.exists():
        raise TypeCheckError(f"env file not found: {env_file}")
    for type_name in schema.values():
        if type_name not in _TYPES:
            raise TypeCheckError(
                f"unknown type {type_name!r}; valid types: {sorted(_TYPES)}"
            )
    values = _parse_env(env_file.read_text())
    issues: List[TypeIssue] = []
    for key, type_name in schema.items():
        if key not in values:
            continue  # missing keys are handled by env_validate
        err = _check_value(values[key], type_name)
        if err:
            issues.append(TypeIssue(key, values[key], type_name, err))
    return TypeCheckResult(issues=issues)
