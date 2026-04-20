# `envault encode` / `envault decode`

Base64-encode or decode the values in your `.env` file in-place or to a
separate destination file.

## Usage

```
envault encode [--dest FILE] [--keys KEY ...]
envault decode [--dest FILE] [--keys KEY ...]
```

## Options

| Flag | Description |
|------|-------------|
| `--dest FILE` | Write output to `FILE` instead of modifying the source in-place. |
| `--keys KEY …` | Only encode/decode the listed keys; leave all other values untouched. |

## Examples

### Encode all values in-place

```bash
envault encode
```

### Encode only specific keys

```bash
envault encode --keys API_KEY DATABASE_URL
```

### Encode to a separate file

```bash
envault encode --dest .env.b64
```

### Decode back to plain text

```bash
envault decode
```

## Notes

- Surrounding single or double quotes are stripped from a value before it is
  encoded, so `KEY="hello"` is encoded as if the value were `hello`.
- Blank lines and comment lines (starting with `#`) are preserved unchanged.
- `encode` followed by `decode` is a lossless round-trip for plain ASCII
  values.  Multi-byte UTF-8 values are also handled correctly.
- The `--dest` flag leaves the original file untouched, which is useful for
  previewing the result before committing.
