# `envault replace` — Find-and-replace values in a `.env` file

The `replace` command performs a find-and-replace operation on the **values**
of keys inside a `.env` file without touching comments or blank lines.

## Usage

```
envault replace <pattern> <replacement> [options]
```

### Positional arguments

| Argument | Description |
|---|---|
| `pattern` | Regex (or literal string) to search for in values. |
| `replacement` | String to substitute matched text with. |

### Options

| Flag | Description |
|---|---|
| `--file PATH` | Source `.env` file. Defaults to the path in `.envault.json`. |
| `--dest PATH` | Write output to this file instead of modifying in place. |
| `--keys K1,K2` | Restrict replacements to a comma-separated list of keys. |
| `--literal` | Treat `pattern` as a plain string, not a regular expression. |
| `--count N` | Maximum number of substitutions per line (`0` = unlimited). |
| `--config PATH` | Path to `.envault.json` (default: `.envault.json`). |

## Examples

### Replace a hostname across all values

```bash
envault replace localhost db.prod.internal
```

### Upgrade a URL scheme (regex)

```bash
envault replace 'http://' 'https://'
```

### Replace only in specific keys

```bash
envault replace old_secret new_secret --keys SECRET_KEY,API_SECRET
```

### Write result to a new file (non-destructive)

```bash
envault replace dev prod --dest .env.prod
```

### Literal replacement (no regex interpretation)

```bash
envault replace '1.2.3' '2.0.0' --literal
```

## Notes

- Quoted values are unquoted before matching; the replacement is written
  without surrounding quotes.
- Comments (`# …`) and blank lines are preserved unchanged.
- The command prints the number of lines modified or a notice when nothing
  matched.
