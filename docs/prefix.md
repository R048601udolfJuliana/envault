# envault prefix-add / prefix-strip

Add or remove a string prefix from every key in your `.env` file.

## Usage

```
envault prefix-add <PREFIX> [--file FILE] [--dest DEST] [--config CONFIG]
envault prefix-strip <PREFIX> [--file FILE] [--dest DEST] [--config CONFIG]
```

### Arguments

| Argument | Description |
|---|---|
| `PREFIX` | The prefix string to add or remove |
| `--file` | Source `.env` file (defaults to value in `.envault.json`) |
| `--dest` | Output file path (default: in-place) |
| `--config` | Path to `.envault.json` (default: `.envault.json`) |

## Examples

### Add a prefix

```bash
# Before: DB_HOST=localhost
envault prefix-add MYAPP_
# After:  MYAPP_DB_HOST=localhost
```

Keys already carrying the prefix are left unchanged.

### Strip a prefix

```bash
# Before: MYAPP_DB_HOST=localhost
envault prefix-strip MYAPP_
# After:  DB_HOST=localhost
```

Keys that do not start with the prefix are preserved as-is.

### Write to a separate file

```bash
envault prefix-add STAGING_ --file .env --dest .env.staging
```

The original file is not modified when `--dest` is provided.

## Notes

- Comment lines (`# …`) and blank lines are preserved verbatim.
- Lines without an `=` sign are passed through unchanged.
- An empty prefix string is rejected with an error.
