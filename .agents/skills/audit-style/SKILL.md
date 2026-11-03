---
name: audit-style
description: Review Python source against this repository's style and documentation guides and produce advisory findings. Use for a requested style audit, not as a required step for every code edit.
---

# Review Python style

Read [Code Style](../../../docs/STYLE.md) and
[Documentation](../../../docs/DOCUMENTATION.md). Follow [AGENTS.md](../../../AGENTS.md)
for the repository environment and validation commands.

## Run the audit

From the repository root, run:

```console
uv run python .agents/skills/audit-style/scripts/audit_style.py --target pipescaler --output local/style_notes.md
```

Set `--target` to the requested Python file or directory. Keep generated reports
under `local/` unless the user chooses another destination. The script parses
source without importing or executing it and does not change audited files.

Review the report against the owning guides. Identify the affected file, concrete
rule, and reason each finding matters; distinguish clear violations from items
requiring judgment. A failed command is an incomplete audit, not a clean result.

## Interpret the result

The report checks:

- Two-line copyright syntax, module/future-import requirements, docstring presence
  for modules, callables, classes, and public class attributes, and signature annotations.
- Import locality and class-looking package facade exports.
- `__all__` presence/formatting and direct public declaration membership in a
  single unmodified literal export collection.
- Direct function and recognizable method ordering, and common capitalized prose
  openings in argument, return, and yield descriptions.
- Literal `.format()`/`%` interpolation, `print` outside recognized CLI locations,
  path naming inferred from annotations or suffixes, and double backticks.

These AST/text checks are advisory. They do not resolve import/decorator identities,
verify copyright history, or establish complete documentation and API intent.
Dynamic exports, constants/imported aliases, conditional definitions, overloads,
property accessors, unknown decorators, possible type names, path meanings, and
intentional command output still need review. Header checks accept a four-digit
single year or range; preserve established start years when editing source.

No findings does not certify full compliance. This audit does not replace Ruff,
type checking, or tests. If the user also asks for fixes, make those edits separately
and validate changed files under AGENTS.md.
