# envault cast

Cast `.env` values to typed Python objects and print them as JSON.

## Usage

```
envault cast [--file PATH] [--hint KEY:TYPE ...]
```

## Options

| Flag | Description |
|------|-------------|
| `--file PATH` | Path to the `.env` file to read (overrides config). |
| `--hint KEY:TYPE` | Declare the type for a specific key. Repeatable. |

## Supported Types

| Type | Description | Example raw value |
|------|-------------|-------------------|
| `str` | Plain string (default) | `hello` |
| `int` | Integer | `8080` |
| `float` | Floating-point number | `3.14` |
| `bool` | Boolean (`true/yes/1/on` → `True`) | `true` |
| `list` | Comma-separated list of strings | `a,b,c` |

## Example

Given `.env`:

```dotenv
PORT=8080
DEBUG=true
HOSTS=api.example.com,cdn.example.com
APP_NAME=myapp
```

Run:

```bash
envault cast \
  --hint PORT:int \
  --hint DEBUG:bool \
  --hint HOSTS:list
```

Output:

```json
{
  "PORT": 8080,
  "DEBUG": true,
  "HOSTS": ["api.example.com", "cdn.example.com"],
  "APP_NAME": "myapp"
}
```

Keys without a `--hint` are returned as plain strings.

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Config error, missing file, or cast failure |
