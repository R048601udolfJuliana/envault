# envault lint

The `lint` subcommand checks a `.env` file for common formatting and consistency issues before you encrypt or share it with your team.

## Usage

```bash
envault lint [FILE] [--strict]
```

| Argument | Default | Description |
|----------|---------|-------------|
| `FILE`   | `.env`  | Path to the `.env` file to check. |
| `--strict` | off | Exit with code `1` if any issues are found. |

## Issue Codes

| Code  | Severity | Description |
|-------|----------|-------------|
| E001  | Error    | Line is not a valid `KEY=VALUE` pair. |
| E002  | Error    | Key name contains invalid characters (must match `[A-Za-z_][A-Za-z0-9_]*`). |
| W001  | Warning  | Duplicate key — the same key appears more than once. |
| W002  | Warning  | Key has an empty value. |

## Examples

### Clean file

```bash
$ envault lint .env
No issues found.
```

### File with issues

```bash
$ envault lint .env
Line 3 [W002]: Key 'DATABASE_URL' has an empty value
Line 7 [W001]: Duplicate key 'API_KEY' (first seen on line 2)
2 issue(s) found.
```

### CI enforcement with `--strict`

```bash
$ envault lint .env --strict
Line 3 [W002]: Key 'DATABASE_URL' has an empty value
1 issue(s) found.
$ echo $?
1
```

Use `--strict` in CI pipelines to block commits that contain malformed `.env` files.
