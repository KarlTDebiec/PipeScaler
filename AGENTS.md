# Instructions

Before planning or coding, read [Architecture](docs/ARCHITECTURE.md),
[Code Style](docs/STYLE.md), and [Documentation](docs/DOCUMENTATION.md).
Apply the relevant conventions to changed files without unrelated refactoring.
Never add or retain compatibility shims. Update callers and remove obsolete APIs
and import paths when changing interfaces.

## Tools

Use `uv run` for repository tools. On Unix, set a writable cache with
`UV_CACHE_DIR=/tmp/uv-cache`. In PowerShell, set it before running tools:

```powershell
$env:UV_CACHE_DIR = Join-Path $env:TEMP "uv-cache"
uv run pytest
```

For commands that emit non-ASCII output, configure Python and PowerShell for UTF-8:

```powershell
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$OutputEncoding = [System.Text.UTF8Encoding]::new()
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
```

## Validation

- Check changed files against the style and documentation guides before running
  tools. Run these checks on **only the Python files changed or requested**:
  1. `uv run ruff format <files>`
  2. `uv run ruff check --fix <files>`
  3. `uv run ty check <files>`
- Run relevant tests with `uv run pytest`; the full suite works from the repository
  root or `test/`. Keep tests requiring serial execution serial.
- You may run pytest with a timeout of up to ten minutes without asking.
- Confirm before expanding lint or type fixes into major refactoring outside the
  requested scope.
- Do not commit binary files. Generate any new binary test assets with scripts
  under `test/scripts/`.

## Version Control

Follow [Contributing](docs/CONTRIBUTING.md) for branches, PR descriptions, and
[CI usage](docs/CONTRIBUTING.md#ci-usage).
