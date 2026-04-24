# envault protect

Mark individual `.env` keys as **protected** (read-only).  Protected keys
cannot be silently overwritten by `set`, `patch`, or `import` commands unless
`--force` is explicitly supplied.

The protection list is stored in `<vault_dir>/.envault_protected.json` as a
sorted JSON array of key names.

---

## Commands

### `envault protect add <KEY>`

Add `KEY` to the protected list.

```bash
envault protect add DB_PASSWORD
# [envault] 'DB_PASSWORD' is now protected.
```

### `envault protect remove <KEY>`

Remove `KEY` from the protected list.

```bash
envault protect remove DB_PASSWORD
# [envault] 'DB_PASSWORD' is no longer protected.
```

### `envault protect list`

Print all currently protected keys.

```bash
envault protect list
  API_KEY
  DB_PASSWORD
  SECRET_KEY
```

---

## Programmatic usage

```python
from pathlib import Path
from envault.env_protect import protect_key, check_protected, ProtectError

vault_dir = Path(".vault")
protect_key(vault_dir, "SECRET_KEY")

try:
    check_protected(vault_dir, ["SECRET_KEY"])
except ProtectError as e:
    print(e)  # The following keys are protected …

# Bypass protection
check_protected(vault_dir, ["SECRET_KEY"], force=True)  # no exception
```

---

## Notes

- Protection is enforced at the **library level**; individual commands must
  call `check_protected()` before writing.
- The sidecar file is intentionally human-readable so it can be committed to
  version control alongside `.envault.json`.
- Adding the same key twice is idempotent.
