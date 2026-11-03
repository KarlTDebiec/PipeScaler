---
name: audit-module-hierarchy
description: Review package dependency hierarchies and sibling cycles when investigating imports, moving modules, or checking architecture declarations. Infer minimum levels as evidence without replacing declared policy.
---

# Review package hierarchies

Read [Architecture](../../../docs/ARCHITECTURE.md) and the relevant package
`__init__.py` declarations. Follow [AGENTS.md](../../../AGENTS.md) for the environment
and validation commands. Declared levels are architectural policy: fewer imports
do not authorize lowering them.

## Run the audit

From the repository root, run:

```console
uv run python .agents/skills/audit-module-hierarchy/scripts/audit_module_hierarchy.py --target pipescaler
```

Use a nested package as `--target` for a narrower review. The script recursively
analyzes package children; `--min-children` selects the minimum child count, with
2 as the default. Use 1 when single-child packages matter to the request.

The script parses imports without executing source. It reports inferred minimum
dependency levels and sibling cycles to stdout without rewriting declarations.
A failed parse or unreadable file makes the audit incomplete.

## Review the evidence

Compare inferred dependencies with declared levels. Preserve intentional
separation even when the graph permits fewer levels. A cycle is a violation, not
permission to call its members independent peers. The script groups cycles only
for diagnosis; do not copy those groups into a valid hierarchy.

Static imports are evidence, not a complete runtime dependency model. Dynamic
imports and class re-exports through facades may need manual review. Export and
import-policy enforcement belongs to the architecture tests:

```console
uv run pytest test/test_module_hierarchy.py
```

Report the scope, actual declaration violations or cycles, and any uncertainty.
If changes are requested, explain the architectural decision and validate changed
Python files under AGENTS.md. Do not rewrite hierarchy levels merely to match the
inferred minimums.
