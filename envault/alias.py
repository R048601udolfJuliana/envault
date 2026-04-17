"""Manage short aliases for encrypted env profiles."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict


class AliasError(Exception):
    pass


def _aliases_path(config_dir: Path) -> Path:
    return config_dir / "aliases.json"


def load_aliases(config_dir: Path) -> Dict[str, str]:
    path = _aliases_path(config_dir)
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise AliasError(f"Corrupt aliases file: {exc}") from exc
    if not isinstance(data, dict):
        raise AliasError("aliases.json must be a JSON object")
    return data


def save_aliases(config_dir: Path, aliases: Dict[str, str]) -> None:
    _aliases_path(config_dir).write_text(json.dumps(aliases, indent=2))


def add_alias(config_dir: Path, name: str, target: str) -> None:
    if not name.strip():
        raise AliasError("Alias name must not be empty")
    aliases = load_aliases(config_dir)
    if name in aliases:
        raise AliasError(f"Alias '{name}' already exists (use --force to overwrite)")
    aliases[name] = target
    save_aliases(config_dir, aliases)


def remove_alias(config_dir: Path, name: str) -> None:
    aliases = load_aliases(config_dir)
    if name not in aliases:
        raise AliasError(f"Alias '{name}' not found")
    del aliases[name]
    save_aliases(config_dir, aliases)


def resolve_alias(config_dir: Path, name: str) -> str:
    aliases = load_aliases(config_dir)
    if name not in aliases:
        raise AliasError(f"Alias '{name}' not found")
    return aliases[name]
