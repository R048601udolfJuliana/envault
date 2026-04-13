# Tag Management

envault supports tagging encrypted `.env` files so you can group and filter them by purpose, environment, or any label you choose.

Tags are stored in `.envault_tags.json` in the working directory. This file should be committed to version control alongside your encrypted files.

## Commands

### Add a tag

```bash
envault tag add <tag> <file>
```

Example:

```bash
envault tag add production secrets.env.gpg
```

### Remove a tag

```bash
envault tag remove <tag> <file>
```

Example:

```bash
envault tag remove production secrets.env.gpg
```

### List tags

List all tags and their associated files:

```bash
envault tag list
```

List files for a specific tag:

```bash
envault tag list production
```

## Storage format

Tags are stored as a JSON object mapping tag names to lists of filenames:

```json
{
  "ci": ["ci.env.gpg"],
  "production": ["prod.env.gpg", "secrets.env.gpg"]
}
```

## Notes

- Tag names must be non-empty strings.
- The same file can carry multiple tags.
- Removing the last file from a tag deletes the tag entry entirely.
- Use `--directory` to specify a non-current working directory.
