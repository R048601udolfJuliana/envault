# envault audit-export

Export the envault audit log to an external file for archival, compliance, or review.

## Usage

```
envault audit-export <output> [--format json|csv|text] [--limit N]
```

### Arguments

| Argument | Description |
|---|---|
| `output` | Destination file path |
| `--format` | Output format: `json` (default), `csv`, or `text` |
| `--limit N` | Export only the last N entries |

## Formats

### json

Outputs a JSON array of audit entry objects:

```json
[
  {"timestamp": "2024-01-15T10:30:00", "action": "push", "actor": "alice", "detail": "pushed .env"}
]
```

### csv

Outputs a CSV file with columns: `timestamp`, `action`, `actor`, `detail`.

### text

Outputs human-readable lines:

```
[2024-01-15T10:30:00] push by alice: pushed .env
```

## Examples

```bash
# Export full audit log as JSON
envault audit-export audit_full.json

# Export last 50 entries as CSV
envault audit-export recent.csv --format csv --limit 50

# Export as plain text for quick review
envault audit-export audit.txt --format text
```

## Notes

- The audit log is stored at `.envault_audit.jsonl` relative to the project base directory.
- If no entries exist, the command exits with an error.
- Use `--limit` to restrict large logs for faster exports.
