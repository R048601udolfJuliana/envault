"""Lint .env files for common issues (duplicates, missing values, bad format)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


class LintError(Exception):
    """Raised when linting cannot proceed (e.g. file not found)."""


@dataclass
class LintIssue:
    line_no: int
    code: str
    message: str

    def __str__(self) -> str:
        return f"Line {self.line_no} [{self.code}]: {self.message}"


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.issues) == 0

    def summary(self) -> str:
        if self.ok:
            return "No issues found."
        lines = [str(issue) for issue in self.issues]
        lines.append(f"{len(self.issues)} issue(s) found.")
        return "\n".join(lines)


_KEY_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


def lint_env(path: Path) -> LintResult:
    """Lint an .env file and return a LintResult with any issues."""
    if not path.exists():
        raise LintError(f"File not found: {path}")

    result = LintResult()
    seen_keys: dict[str, int] = {}

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise LintError(f"Could not read file: {path}: {exc}") from exc

    for line_no, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()

        # Skip blanks and comments
        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            result.issues.append(
                LintIssue(line_no, "E001", f"Line is not a valid KEY=VALUE pair: {raw!r}")
            )
            continue

        key, _, value = line.partition("=")
        key = key.strip()

        if not _KEY_RE.match(key):
            result.issues.append(
                LintIssue(line_no, "E002", f"Invalid key name: {key!r}")
            )

        if key in seen_keys:
            result.issues.append(
                LintIssue(
                    line_no,
                    "W001",
                    f"Duplicate key {key!r} (first seen on line {seen_keys[key]})",
                )
            )
        else:
            seen_keys[key] = line_no

        if value.strip() == "":
            result.issues.append(
                LintIssue(line_no, "W002", f"Key {key!r} has an empty value")
            )

    return result
