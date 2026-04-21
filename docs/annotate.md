# envault annotate

The `annotate` feature lets you attach **inline type hints and descriptions** to keys in your `.env` file. Annotations are stored as structured comments directly above the key line.

## Format

```
# @type:string  @desc:Primary database hostname
DB_HOST=localhost
```

Both `@type` and `@desc` are optional, but at least one must be supplied.

---

## Commands

### `envault annotate-set`

Add or replace an annotation for a specific key.

```bash
envault annotate-set DB_HOST --type string --desc "Primary database hostname"
```

**Options**

| Flag | Description |
|------|-------------|
| `KEY` | The `.env` key to annotate |
| `--type TYPE` | Type hint (e.g. `string`, `int`, `bool`, `url`) |
| `--desc DESC` | Human-readable description |
| `--dest FILE` | Write output to a separate file (default: in-place) |
| `--config FILE` | Path to `.envault.json` (default: `.envault.json`) |

If the key already has an annotation comment immediately above it, the existing annotation is **replaced**.

---

### `envault annotate-list`

Print all annotated keys and their metadata.

```bash
envault annotate-list
```

Example output:

```
DB_HOST:   type=string  desc=Primary database hostname
DB_PORT:   type=int  desc=Port number
SECRET_KEY:   type=string
```

---

## Use cases

- **Onboarding** – help new team members understand what each variable does without leaving the `.env` file.
- **Validation** – pair with `envault policy` to enforce type constraints.
- **Documentation generation** – parse annotations programmatically via `read_annotations(path)`.
