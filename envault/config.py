"""Configuration management for envault."""

import json
from pathlib import Path
from typing import Optional

CONFIG_FILENAME = ".envault.json"


class ConfigError(Exception):
    """Raised when configuration is invalid or missing."""
    pass


class EnvaultConfig:
    """Represents the envault project configuration."""

    def __init__(self, env_file: str, recipients: list[str], encrypted_file: Optional[str] = None):
        self.env_file = env_file
        self.recipients = recipients
        self.encrypted_file = encrypted_file or f"{env_file}.gpg"

    def to_dict(self) -> dict:
        return {
            "env_file": self.env_file,
            "recipients": self.recipients,
            "encrypted_file": self.encrypted_file,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EnvaultConfig":
        required = {"env_file", "recipients"}
        missing = required - data.keys()
        if missing:
            raise ConfigError(f"Missing required config keys: {missing}")
        return cls(
            env_file=data["env_file"],
            recipients=data["recipients"],
            encrypted_file=data.get("encrypted_file"),
        )


def load_config(directory: Path = Path(".")) -> EnvaultConfig:
    """
    Load envault config from a directory.

    Raises:
        ConfigError: If config file is missing or malformed.
    """
    config_path = directory / CONFIG_FILENAME
    if not config_path.exists():
        raise ConfigError(
            f"No {CONFIG_FILENAME} found in {directory}. Run 'envault init' first."
        )
    try:
        data = json.loads(config_path.read_text())
    except json.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON in {CONFIG_FILENAME}: {e}") from e
    return EnvaultConfig.from_dict(data)


def save_config(config: EnvaultConfig, directory: Path = Path(".")) -> None:
    """
    Save envault config to a directory.

    Raises:
        ConfigError: If the file cannot be written.
    """
    config_path = directory / CONFIG_FILENAME
    try:
        config_path.write_text(json.dumps(config.to_dict(), indent=2) + "\n")
    except OSError as e:
        raise ConfigError(f"Failed to write {CONFIG_FILENAME}: {e}") from e
