# `envault status`

Display a summary of the current vault state, including the `.env` file, encrypted output, manifest integrity, and registered recipients.

## Usage

```bash
envault status [--exit-code]
```

## Options

| Flag | Description |
|------|-------------|
| `--exit-code` | Exit with a non-zero code if the vault is unhealthy |

## Exit Codes (with `--exit-code`)

| Code | Meaning |
|------|---------|
| `0`  | Vault is healthy |
| `2`  | Encrypted file is missing |
| `3`  | Manifest exists but SHA-256 does not match the encrypted file |

## Example Output

```
envault status
========================================
  [✓] .env file        : .env
  [✓] encrypted file   : .env.gpg
      sha256           : 3a7bd3e2160...
  [✓] manifest         : .env.manifest
  recipients (2):
      • alice@example.com
      • bob@example.com
```

## Notes

- The manifest check compares the SHA-256 of the encrypted file against the value stored in `.env.manifest` (written by `envault verify --write`).
- Recipients are loaded from `.envault-recipients.json` in the same directory as the `.env` file.
- Use `--exit-code` in CI pipelines to assert vault integrity before deployment.
