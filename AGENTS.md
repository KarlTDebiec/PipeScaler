# Instructions

Review [docs/STYLE.md](/docs/STYLE.md) and [docs/ARCHITECTURE.md](/docs/ARCHITECTURE.md) before planning or coding.

## Tools

* This repository uses a virtual environment. To activate the venv in your shell: `source .venv/bin/activate`.
* This repository uses `uv`. Use `UV_CACHE_DIR=/tmp/uv-cache uv run` when executing tools.

### Version Control

* Branches should be named in the format `feature/brief-description`.
* Interact with GitHub using the GitHub MCP; do not use the `gh` CLI.

### Linting

* Before running `ruff` or `ty`, check changed files for compliance with [docs/STYLE.md](/docs/STYLE.md).
* Run the following checks on **only the Python files you have changed or been asked to**:
  1. `UV_CACHE_DIR=/tmp/uv-cache uv run ruff format`
  2. `UV_CACHE_DIR=/tmp/uv-cache uv run ruff check --fix`
  3. `UV_CACHE_DIR=/tmp/uv-cache uv run ty check`
* If `ruff` or `ty` suggest changes that would require major refactoring, confirm with the user before proceeding.

### Testing

* Run the tests as follows:
  * `cd test && UV_CACHE_DIR=/tmp/uv-cache uv run pytest`
* You may run pytest with a timeout of up to 10 minutes without asking the user.

## Code Style

Follow [docs/STYLE.md](/docs/STYLE.md). Key points:

* Include the standard copyright header and module docstring at the top of each Python file.
* Include `from __future__ import annotations` in Python modules that contain imports, exports, type annotations, functions, or classes.
* Include type annotations for all function and method signatures, except omit the return type annotation when a function always returns `None`.
* Use the `logging` module rather than `print` for user-facing output in scripts or libraries. CLI tools may use `print` for intentional stdout command output.
* Keep class members and module functions ordered as described in the style guide.

## Documentation

* Use Markdown for repository documentation.
* Do **not** include any reStructuredText markup such as double backticks.
* Provide Google-style docstrings for all modules, classes, properties, and functions, including internal helpers prefixed with an underscore.
