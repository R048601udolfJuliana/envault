"""Profile management for envault — named environment configurations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


class ProfileError(Exception):
    """Raised when a profile operation fails."""


_PROFILES_FILE = ".envault_profiles.json"


def _profiles_path(base_dir: Path) -> Path:
    return base_dir / _PROFILES_FILE


def load_profiles(base_dir: Path) -> Dict[str, dict]:
    """Load all profiles from the profiles file. Returns empty dict if missing."""
    path = _profiles_path(base_dir)
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ProfileError(f"Invalid profiles file: {exc}") from exc
    if not isinstance(data, dict):
        raise ProfileError("Profiles file must contain a JSON object.")
    return data


def save_profiles(base_dir: Path, profiles: Dict[str, dict]) -> None:
    """Persist profiles to disk."""
    _profiles_path(base_dir).write_text(
        json.dumps(profiles, indent=2), encoding="utf-8"
    )


def add_profile(
    base_dir: Path,
    name: str,
    env_file: str,
    encrypted_file: Optional[str] = None,
    recipients_file: Optional[str] = None,
) -> Dict[str, dict]:
    """Add or overwrite a named profile. Returns updated profiles dict."""
    if not name or not name.strip():
        raise ProfileError("Profile name must not be empty.")
    profiles = load_profiles(base_dir)
    profiles[name] = {
        "env_file": env_file,
        "encrypted_file": encrypted_file or f"{env_file}.gpg",
        "recipients_file": recipients_file or ".envault_recipients.json",
    }
    save_profiles(base_dir, profiles)
    return profiles


def remove_profile(base_dir: Path, name: str) -> Dict[str, dict]:
    """Remove a profile by name. Raises ProfileError if not found."""
    profiles = load_profiles(base_dir)
    if name not in profiles:
        raise ProfileError(f"Profile '{name}' not found.")
    del profiles[name]
    save_profiles(base_dir, profiles)
    return profiles


def get_profile(base_dir: Path, name: str) -> dict:
    """Retrieve a single profile by name. Raises ProfileError if not found."""
    profiles = load_profiles(base_dir)
    if name not in profiles:
        raise ProfileError(f"Profile '{name}' not found.")
    return profiles[name]


def list_profile_names(base_dir: Path) -> List[str]:
    """Return sorted list of profile names."""
    return sorted(load_profiles(base_dir).keys())
