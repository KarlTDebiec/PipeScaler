---
name: audit-module-hierarchy
description: Audit declared package hierarchies and exports against actual imports, using inferred minimum levels as review evidence and reporting cycles. Use when package structure changes or hierarchy declarations may be stale.
---

# Audit `__init__.py` Hierarchy and Exports

Follow [Architecture](../../docs/ARCHITECTURE.md). Declared levels are architectural
policy; inferred minimum levels do not automatically replace them.

## When to use

- A module was moved or renamed.
- A package hierarchy comment looks stale.
- `__all__` ordering is inconsistent with current structure.
- You suspect dependency cycles between sibling modules/packages.

## Goals

- Keep hierarchy comments truthful: "modules may import from any above."
- Preserve declared levels unless a deliberate architectural change is justified.
- Group peers on the same line with ` / `.
- Report sibling cycles explicitly.
- Keep `__all__` aligned with imported/exported symbols and existing style.

## Quick workflow

1. Identify `__init__.py` files:
   - `pipescaler/__init__.py` (top-level package hierarchy)
   - nested package `__init__.py` files
2. Run the helper script:
   - `uv run python skills/audit-module-hierarchy/scripts/audit_module_hierarchy.py --target pipescaler`
3. Review output:
   - proposed levels per package
   - detected cycles
4. Compare inferred levels to declarations. Explain any intentional hierarchy change.
5. Run `uv run pytest test/test_module_hierarchy.py` to check declarations and imports.
6. Run validation on changed Python files:
   - `uv run ruff format <changed_files>`
   - `uv run ruff check --fix <changed_files>`
   - `uv run ty check <changed_files>`

## Ordering rules

- Build edges as `importer -> importee`.
- The report collapses strongly connected components (SCCs) for diagnosis; cycles
  must be resolved rather than legalized as same-level peers.
- Assign each SCC level as:
  - `1` if it imports no sibling/module in scope
  - otherwise `1 + max(level(imported_scc))`
- Render levels ascending (dependencies first).
- For display, join same-level SCC members using ` / `.
- Report cycles as architecture violations; do not group them as independent peers.

## Scope guidance

- For repository-wide architecture, analyze top-level packages under `pipescaler/`.
- For local package docs, analyze direct children of that package only.
- Do not infer ordering from filenames; only from imports.

## Reporting guidance

When done, report:

- which `__init__.py` files were updated
- the new hierarchy levels
- any detected cycles
- whether validation checks passed
