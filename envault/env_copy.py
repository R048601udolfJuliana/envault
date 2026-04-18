"""Copy (clone) an encrypted vault to a new destination path."""
from __future__ import annotations

import shutil
from pathlib import Path


class CopyError(Exception):
    """Raised when a vault copy operation fails."""


def copy_vault(
    source: Path,
    destination: Path,
    *,
    force: bool = False,
    include_manifest: bool = True,
) -> Path:
    """Copy *source* encrypted file to *destination*.

    Parameters
    ----------
    source:
        Path to the existing ``.env.gpg`` file.
    destination:
        Target path for the copy.
    force:
        Overwrite *destination* if it already exists.
    include_manifest:
        Also copy the accompanying ``.manifest`` file when present.

    Returns
    -------
    Path
        The resolved destination path.
    """
    source = Path(source)
    destination = Path(destination)

    if not source.exists():
        raise CopyError(f"Source file not found: {source}")

    if destination.exists() and not force:
        raise CopyError(
            f"Destination already exists: {destination}. Use force=True to overwrite."
        )

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)

    if include_manifest:
        manifest = source.with_suffix(".manifest")
        if manifest.exists():
            dest_manifest = destination.with_suffix(".manifest")
            shutil.copy2(manifest, dest_manifest)

    return destination
