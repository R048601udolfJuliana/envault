# envault mask

Mask sensitive values in a `.env` file for safe display, logging, or sharing.

## Usage

```
envault mask [options]
```

## Options

| Flag | Description |
|------|-------------|
| `--source FILE` | Source `.env` file (default: from config) |
| `--output FILE` | Write masked output to this file |
| `--keys k1,k2` | Comma-separated list of keys to always mask |
| `--placeholder TEXT` | Replacement string (default: `***`) |
| `--no-auto` | Disable auto-detection of sensitive key names |

## Auto-detection

By default, keys whose names contain any of the following substrings
(case-insensitive) are masked:

`secret`, `password`, `passwd`, `token`, `key`, `api`, `auth`, `private`, `credential`

## Examples

Print which keys were masked (no file written):

```bash
envault mask
```

Write a masked copy to `safe.env`:

```bash
envault mask --output safe.env
```

Mask specific keys regardless of name:

```bash
envault mask --keys CUSTOM_VAR,ANOTHER_VAR --no-auto
```

Use a custom placeholder:

```bash
envault mask --placeholder "<hidden>" --output safe.env
```
