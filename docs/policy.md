# envault policy

The `policy` feature lets teams define rules that `.env` files must satisfy before encryption or deployment.

## Commands

### `envault policy-add <KEY>`

Add a policy rule for a specific key.

```bash
envault policy-add DATABASE_URL --min-length 20
envault policy-add SECRET_KEY --pattern "[A-Z0-9]{32}"
envault policy-add DEBUG --optional
```

Options:
- `--optional` — key is not required to be present
- `--min-length N` — value must be at least N characters
- `--pattern REGEX` — value must match the given regular expression
- `--config-dir DIR` — directory containing the policy file (default: `.`)

### `envault policy-list`

List all defined policy rules.

```bash
envault policy-list
```

### `envault policy-check`

Check the current `.env` file against all defined rules.

```bash
envault policy-check
envault policy-check --env-file .env.production
```

Exits with code `1` if any violations are found.

## Policy file

Rules are stored in `.envault_policy.json` in the config directory:

```json
[
  {"key": "DATABASE_URL", "required": true, "min_length": 20, "pattern": null},
  {"key": "SECRET_KEY", "required": true, "min_length": null, "pattern": "[A-Z0-9]{32}"}
]
```

## Integration

Run `policy-check` as part of your CI pipeline or as a git pre-commit hook via `envault hook-install`.
