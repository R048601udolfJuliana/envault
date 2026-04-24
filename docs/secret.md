# envault secret

Scan a `.env` file for potential secrets, sensitive key names, or high-entropy values.

## Usage

```
envault secret [--file PATH] [--no-entropy] [--no-names] [--strict]
```

## Options

| Flag | Description |
|------|-------------|
| `--file PATH` | Path to `.env` file. Defaults to the value in `.envault.json`. |
| `--no-entropy` | Disable entropy-based secret detection. |
| `--no-names` | Disable sensitive key-name pattern matching. |
| `--strict` | Exit with code `1` if any secrets are detected. |

## Detection methods

### Sensitive key names

Keys matching patterns such as `password`, `secret`, `token`, `api_key`,
`auth`, `private_key`, or `credentials` (case-insensitive) are flagged
regardless of their value.

### High-entropy values

Values with 8 or more characters and a Shannon entropy ≥ 3.5 bits are
considered potentially secret (e.g. random tokens, hashed passwords).

## Example

```
$ envault secret
Detected 2 potential secret(s):
  API_KEY=ab***  (sensitive key name)
  RANDOM_VAR=xB***  (high entropy (3.72))
```

```
$ envault secret --no-entropy
Detected 1 potential secret(s):
  API_KEY=ab***  (sensitive key name)
```

## Exit codes

| Code | Meaning |
|------|---------|
| `0`  | Scan completed (findings may exist unless `--strict` is used). |
| `1`  | Error loading config, reading file, or secrets found with `--strict`. |
