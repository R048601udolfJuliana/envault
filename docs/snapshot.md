# Snapshot Management

envault lets you save named snapshots of your encrypted `.env` file so you can roll back to a known-good state at any time.

## Commands

### Save a snapshot

```bash
envault snapshot save <name>
```

Saves the current encrypted file as a snapshot with the given name. Snapshots are stored in `.envault_snapshots/` next to the encrypted file and tracked in a local `snapshots.json` manifest.

**Example:**
```bash
envault snapshot save pre-deploy
```

### List snapshots

```bash
envault snapshot list
```

Prints all saved snapshots with their names and timestamps.

**Example output:**
```
  pre-deploy            2024-06-01T12:00:00+00:00
  release-1.2           2024-06-15T09:30:00+00:00
```

### Restore a snapshot

```bash
envault snapshot restore <name>
```

Replaces the current encrypted file with the contents of the named snapshot. The restored file can then be decrypted with `envault pull`.

**Example:**
```bash
envault snapshot restore pre-deploy
```

### Delete a snapshot

```bash
envault snapshot delete <name>
```

Removes the snapshot file and its metadata entry.

## Storage layout

```
.envault_snapshots/
  snapshots.json          # metadata index
  pre-deploy_2024-...gpg  # snapshot files
```

> **Note:** Snapshot files are binary GPG-encrypted blobs. They should be excluded from version control via `.gitignore` or kept in a secure location.

## Recommended workflow

1. Before a risky change: `envault snapshot save before-migration`
2. Apply changes and push: `envault push`
3. If something goes wrong: `envault snapshot restore before-migration && envault pull`
