"""env_status.py — Report the current status of the vault (encrypted file, recipients, manifest)."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from envault.config import EnvaultConfig
from envault.recipients import load_recipients
from envault.verify import _sha256


class StatusError(Exception):
    """Raised when status cannot be determined."""


@dataclass
class VaultStatus:
    env_file: str
    env_exists: bool
    encrypted_file: str
    encrypted_exists: bool
    manifest_file: str
    manifest_exists: bool
    manifest_ok: Optional[bool]  # None if manifest missing
    recipients: List[str] = field(default_factory=list)
    encrypted_sha256: Optional[str] = None

    def summary_lines(self) -> List[str]:
        lines = []
        env_mark = "✓" if self.env_exists else "✗"
        enc_mark = "✓" if self.encrypted_exists else "✗"
        lines.append(f"  [{env_mark}] .env file        : {self.env_file}")
        lines.append(f"  [{enc_mark}] encrypted file   : {self.encrypted_file}")
        if self.encrypted_exists and self.encrypted_sha256:
            lines.append(f"      sha256           : {self.encrypted_sha256[:16]}...")
        if self.manifest_exists:
            ok_mark = "✓" if self.manifest_ok else "✗"
            lines.append(f"  [{ok_mark}] manifest         : {self.manifest_file}")
        else:
            lines.append(f"  [–] manifest         : {self.manifest_file} (missing)")
        lines.append(f"  recipients ({len(self.recipients)}):")
        for r in self.recipients:
            lines.append(f"      • {r}")
        if not self.recipients:
            lines.append("      (none)")
        return lines


def get_status(config: EnvaultConfig) -> VaultStatus:
    """Collect status information for the current vault."""
    env_path = Path(config.env_file)
    enc_path = Path(config.encrypted_file)
    manifest_path = enc_path.with_suffix(".manifest")

    enc_sha = None
    if enc_path.exists():
        try:
            enc_sha = _sha256(enc_path)
        except Exception:
            pass

    manifest_ok: Optional[bool] = None
    if manifest_path.exists():
        try:
            import json
            data = json.loads(manifest_path.read_text())
            expected = data.get("sha256")
            manifest_ok = expected is not None and enc_sha == expected
        except Exception:
            manifest_ok = False

    try:
        recipients = load_recipients(Path(config.env_file).parent)
    except Exception:
        recipients = []

    return VaultStatus(
        env_file=str(env_path),
        env_exists=env_path.exists(),
        encrypted_file=str(enc_path),
        encrypted_exists=enc_path.exists(),
        manifest_file=str(manifest_path),
        manifest_exists=manifest_path.exists(),
        manifest_ok=manifest_ok,
        recipients=recipients,
        encrypted_sha256=enc_sha,
    )
