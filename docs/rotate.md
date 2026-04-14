# Key Rotation

`envault rotate` re-encrypts the vault file for a new (or updated) set of GPG
recipients without ever storing the plaintext `.env` on disk longer than
necessary.

## How it works

1. The existing `.env.gpg` is **decrypted** to a temporary file.
2. The plaintext is **re-encrypted** for the new recipient list.
3. The old encrypted file is saved as `.env.bak.gpg` (one-step rollback).
4. The new encrypted file replaces the original `.env.gpg`.
5. The temporary plaintext file is deleted in all cases (even on error).

## Usage

```bash
# Re-encrypt for two new team members (keeps existing file as backup)
envault rotate -r FINGERPRINT1 -r FINGERPRINT2

# Preview what would happen without touching any files
envault rotate -r FINGERPRINT1 --dry-run

# Re-encrypt with the *current* recipient list (e.g. after a key refresh)
envault rotate

# Log the rotation event to an audit file
envault rotate -r FINGERPRINT1 --audit-file .envault-audit.jsonl
```

## Options

| Flag | Description |
|------|-------------|
| `-r / --recipient KEY_ID` | GPG key ID to encrypt for. Repeatable. Defaults to the recipients already stored in `.envault.json`. |
| `--dry-run` | Validate the rotation (decrypt + re-encrypt) without writing any files. |
| `--audit-file PATH` | Append a structured JSON-lines rotation event to *PATH*. |

## Rollback

If a rotation goes wrong, restore the previous vault:

```bash
cp .env.bak.gpg .env.gpg
```

> **Note:** Only one backup is kept at a time. Running `rotate` again will
> overwrite `.env.bak.gpg`. If you need to preserve multiple snapshots,
> copy the backup to a safe location before rotating again.

## Passphrase

If your GPG key is protected by a passphrase, set `ENVAULT_PASSPHRASE` in the
environment before running `rotate`:

```bash
export ENVAULT_PASSPHRASE="your-passphrase"
envault rotate -r NEW_KEY_ID
```

## Audit log format

When `--audit-file` is used, each rotation appends a single JSON line with the
following fields:

```json
{
  "timestamp": "2024-05-01T12:34:56Z",
  "action": "rotate",
  "recipients": ["FINGERPRINT1", "FINGERPRINT2"],
  "dry_run": false
}
```
