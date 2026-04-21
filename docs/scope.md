# envault scope

Filter a `.env` file by **scope prefix** (e.g. `DEV_`, `PROD_`, `TEST_`).  
This lets you maintain a single source-of-truth `.env` and derive environment-specific files automatically.

## Usage

```bash
envault scope <SCOPE> [options]
```

### Arguments

| Argument | Description |
|---|---|
| `SCOPE` | The scope to filter by (e.g. `dev`, `prod`, `test`). Case-insensitive. |

### Options

| Option | Description |
|---|---|
| `--src FILE` | Source `.env` file. Defaults to the file in `.envault.json`. |
| `--dest FILE` | Destination file. Defaults to `.env.<scope>` in the same directory. |
| `--strip-prefix` | Remove the `<SCOPE>_` prefix from matching keys in the output. |
| `--scoped-only` | Drop keys that have no scope prefix at all. |
| `--config FILE` | Config file path (default: `.envault.json`). |

## Examples

### Generate a dev-specific env file

```bash
envault scope dev
# writes .env.dev with DEV_* keys + unscoped keys
```

### Strip prefix in output

```bash
envault scope prod --strip-prefix
# PROD_DB_URL=... becomes DB_URL=... in .env.prod
```

### Keep only scoped keys

```bash
envault scope test --scoped-only --dest .env.test
```

## How it works

A key is considered to belong to scope `X` when it matches `X_<REST>` (case-insensitive).  
Keys with no scope prefix are treated as *unscoped* and are included by default unless `--scoped-only` is set.
