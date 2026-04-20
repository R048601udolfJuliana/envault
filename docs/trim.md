# envault trim

Trim leading and trailing whitespace from `.env` values.

## Usage

```
envault trim [--file PATH] [--dest PATH] [--dry-run] [--config PATH]
```

## Options

| Flag | Description |
|------|-------------|
| `--file PATH` | Source `.env` file. Defaults to the file set in `.envault.json`. |
| `--dest PATH` | Write trimmed output to a separate file instead of editing in-place. |
| `--dry-run` | Report how many lines would change without writing anything. |
| `--config PATH` | Path to the envault config file (default: `.envault.json`). |

## Examples

Trim the default `.env` in-place:

```bash
envault trim
```

Preview changes without modifying the file:

```bash
envault trim --dry-run
```

Write the trimmed result to a new file:

```bash
envault trim --dest .env.clean
```

## Notes

- Comment lines (`# ...`) and blank lines are preserved unchanged.
- Lines without an `=` sign are left untouched.
- Only the *value* portion (right of the first `=`) is trimmed; key names are not modified.
