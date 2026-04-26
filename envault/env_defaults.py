"""Apply default values to missing or empty keys in a .env file."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple


class DefaultsError(Exception):
    """Raised when applying defaults fails."""


def _parse_env(text: str) -> List[Tuple[str, str, str]]:
    """Return list of (key, value, raw_line) for key=value lines."""
    result = []
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            result.append(("", "", line))
            continue
        if "=" not in stripped:
            result.append(("", "", line))
            continue
        key, _, val = stripped.partition("=")
        val = val.strip().strip('"').strip("'")
        result.append((key.strip(), val, line))
    return result


def apply_defaults(
    source: Path,
    defaults: Dict[str, str],
    *,
    dest: Path | None = None,
    overwrite_empty: bool = True,
) -> Tuple[Path, List[str]]:
    """Apply *defaults* to *source*, writing result to *dest*.

    Keys already present (and non-empty unless *overwrite_empty* is True)
    are left unchanged.  Returns ``(dest_path, list_of_applied_keys)``.
    """
    if not source.exists():
        raise DefaultsError(f"Source file not found: {source}")
    if not defaults:
        raise DefaultsError("No defaults provided.")

    dest = dest or source
    text = source.read_text(encoding="utf-8")
    parsed = _parse_env(text)

    existing: Dict[str, str] = {}
    for key, val, _ in parsed:
        if key:
            existing[key] = val

    applied: List[str] = []
    new_lines: List[str] = [line for _, _, line in parsed]

    for def_key, def_val in defaults.items():
        current = existing.get(def_key)
        if current is None:
            # Key not present — append
            new_lines.append(f"{def_key}={def_val}\n")
            applied.append(def_key)
        elif overwrite_empty and current == "":
            # Key present but empty — replace inline
            new_lines = [
                f"{def_key}={def_val}\n"
                if (k == def_key)
                else raw
                for k, _, raw in parsed
            ]
            applied.append(def_key)

    dest.write_text("".join(new_lines), encoding="utf-8")
    return dest.resolve(), applied
