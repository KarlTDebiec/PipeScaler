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

The report checks direct public declarations against a single literal `__all__`,
direct function and recognizable method ordering, and common capitalized prose
openings in argument, return, and yield descriptions.

Dynamic exports, constants and imported aliases, conditional definitions,
overloads, property accessors, unknown decorators, and possible type names still
need review. Decorator names provide syntactic evidence, not resolved runtime
identities. These checks remain advisory; no findings does not establish complete
compliance.

This audit does not replace Ruff, type checking, or tests. If the user also asks
for fixes, make those edits separately and validate changed files under AGENTS.md.
