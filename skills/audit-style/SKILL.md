---
name: audit-style
description: Audit Python files in pipescaler for compliance with docs/STYLE.md and write conservative markdown notes, typically to local/style_notes.md. Use when asked to review repository style compliance without automatically modifying source files.
---

# Audit `docs/STYLE.md` Compliance

Use this workflow to review Python source files against `docs/STYLE.md` and write notes without changing source code.

## Quick workflow

1. Read `docs/STYLE.md`.
2. Run the helper script:
   - `UV_CACHE_DIR=/tmp/uv-cache uv run python skills/audit-style/scripts/audit_style.py --target pipescaler --output local/style_notes.md`
3. Review the generated markdown report.
4. If asked to fix issues, edit source files separately and validate only changed Python files:
   - `UV_CACHE_DIR=/tmp/uv-cache uv run ruff format <changed_files>`
   - `UV_CACHE_DIR=/tmp/uv-cache uv run ruff check --fix <changed_files>`
   - `UV_CACHE_DIR=/tmp/uv-cache uv run ty check <changed_files>`

## Notes

- The script is intentionally conservative and flags items that may require maintainer judgment.
- It does not run `ruff`, `ty`, or tests.
- It reports direct public functions, classes, and explicit type aliases omitted from a single literal `__all__`; it skips dynamic exports. Constants and imported aliases still require public API judgment.
- It checks direct module function groups and class method groups with recognizable decorators, including alphabetical order. Conditional definitions, overload stubs, property accessors, and unknown class decorators require manual review. Decorator names are syntactic evidence, not resolved runtime identities.
- It flags common capitalized prose openings in `Arguments:`, `Returns:`, and `Yields:` descriptions. Unfamiliar words are left for manual review because they may be type names.
- These checks produce advisory notes, not new repository-wide test failures. Review semantics and existing intentional exceptions before applying fixes.
- A report with no notes does not prove compliance with every style or documentation rule, public API intent, or whether `print` output is user-facing.
- Keep generated audit notes under `local/` unless the user asks for a different path.
