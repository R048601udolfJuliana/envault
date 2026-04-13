"""Search for keys within a decrypted .env file."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


class SearchError(Exception):
    """Raised when a search operation fails."""


@dataclass
class SearchMatch:
    """A single match found during a search."""

    line_number: int
    key: str
    value: str

    def __str__(self) -> str:
        return f"  line {self.line_number}: {self.key}={self.value}"


@dataclass
class SearchResult:
    """Aggregated results of a search operation."""

    pattern: str
    matches: List[SearchMatch] = field(default_factory=list)

    @property
    def found(self) -> bool:
        return len(self.matches) > 0

    def summary(self) -> str:
        if not self.found:
            return f"No matches for '{self.pattern}'."
        lines = [f"{len(self.matches)} match(es) for '{self.pattern}':"]
        lines.extend(str(m) for m in self.matches)
        return "\n".join(lines)


def _parse_env(text: str) -> List[tuple[int, str, str]]:
    """Return list of (line_number, key, value) from env text."""
    results: List[tuple[int, str, str]] = []
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            results.append((lineno, key, value))
    return results


def search_env(
    env_file: Path,
    pattern: str,
    *,
    search_values: bool = False,
    case_sensitive: bool = False,
) -> SearchResult:
    """Search *env_file* for keys (and optionally values) matching *pattern*.

    Args:
        env_file: Path to a plaintext .env file.
        pattern: Regular-expression pattern to match against.
        search_values: When True, also match against values.
        case_sensitive: When True, use case-sensitive matching.

    Returns:
        A :class:`SearchResult` with all matches.

    Raises:
        SearchError: If the file cannot be read or the pattern is invalid.
    """
    if not env_file.exists():
        raise SearchError(f"File not found: {env_file}")

    try:
        flags = 0 if case_sensitive else re.IGNORECASE
        compiled = re.compile(pattern, flags)
    except re.error as exc:
        raise SearchError(f"Invalid pattern '{pattern}': {exc}") from exc

    try:
        text = env_file.read_text(encoding="utf-8")
    except OSError as exc:
        raise SearchError(f"Cannot read {env_file}: {exc}") from exc

    result = SearchResult(pattern=pattern)
    for lineno, key, value in _parse_env(text):
        key_match = compiled.search(key)
        value_match = search_values and compiled.search(value)
        if key_match or value_match:
            result.matches.append(SearchMatch(line_number=lineno, key=key, value=value))

    return result
