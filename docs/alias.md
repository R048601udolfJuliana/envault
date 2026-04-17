# Alias Management

Envault lets you define short aliases that map to profile names or target identifiers, making it easier to switch between environments without typing full names.

## Commands

### Add an alias

```bash
envault alias add <name> <target>
envault alias add prod production-profile
```

Use `--force` to overwrite an existing alias:

```bash
envault alias add prod new-production --force
```

### Remove an alias

```bash
envault alias remove <name>
envault alias remove prod
```

### List all aliases

```bash
envault alias list
```

Example output:

```
  dev -> development
  prod -> production
  staging -> staging-env
```

### Resolve an alias

Print the target a given alias points to:

```bash
envault alias resolve prod
# production
```

## Storage

Aliases are stored in `aliases.json` alongside your `.envault.json` config file. The file is a plain JSON object mapping alias names to target strings.

## Notes

- Alias names must be non-empty strings.
- Duplicate aliases are rejected unless `--force` is passed.
- Aliases are resolved locally and are not encrypted.
