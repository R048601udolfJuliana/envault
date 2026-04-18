"""Apply a diff patch to a .env file."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Tuple


class ApplyError(Exception):
    pass


def _parse_env(text: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def apply_additions(env_path: Path, additions: Dict[str, str]) -> List[str]:
    """Add or overwrite keys in a .env file. Returns list of applied keys."""
    if not env_path.exists():
        raise ApplyError(f".env file not found: {env_path}")
    lines = env_path.read_text().splitlines(keepends=True)
    applied: List[str] = []
    remaining = dict(additions)
    new_lines: List[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            if key in remaining:
                new_lines.append(f"{key}={remaining.pop(key)}\n")
                applied.append(key)
                continue
        new_lines.append(line)
    for key, value in remaining.items():
        new_lines.append(f"{key}={value}\n")
        applied.append(key)
    env_path.write_text("".join(new_lines))
    return applied


def apply_removals(env_path: Path, keys: List[str]) -> List[str]:
    """Remove keys from a .env file. Returns list of removed keys."""
    if not env_path.exists():
        raise ApplyError(f".env file not found: {env_path}")
    lines = env_path.read_text().splitlines(keepends=True)
    key_set = set(keys)
    removed: List[str] = []
    new_lines: List[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            if key in key_set:
                removed.append(key)
                continue
        new_lines.append(line)
    env_path.write_text("".join(new_lines))
    return removed
