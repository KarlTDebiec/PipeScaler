# Code Style

## Python and formatting

- Target Python 3.13. Use `uv` and the repository's `pyproject.toml` and `uv.lock`.
- Preserve the standard two-line copyright/license header and its established
  start year. Include a module docstring and `from __future__ import annotations`.
- Let Ruff own formatting and import sorting. Apply conventions to changed code
  without unrelated cleanup.

## Imports and exports

- Use single-dot relative imports for modules and child packages within the
  containing package, such as `from .foo import Bar` or
  `from .child.foo import Bar`.
- Use absolute imports rooted at the concrete owning module when reaching outside
  the containing package. Do not use multi-dot relative imports.
- Public names may be imported from another package's `__init__.py` facade when
  listed in its `__all__`. Within a package subtree, import a name from its owning
  module rather than an ancestor facade that re-exports it.
- Do not import underscore-prefixed names from another project module. Make shared
  project-owned names public and declare them in the owner's `__all__`.
- Use `TYPE_CHECKING` blocks when needed to avoid circular imports. Import required
  dependencies at module scope; make optional dependency boundaries explicit.
- Name dedicated lazy-import helpers `import_<module>[_<symbol_or_purpose>]`
  (private forms start with `_`). Reserve `get_...` for retrieval or caching.
- Declare public module-level functions, classes, and type aliases in `__all__`.
  Include constants and imported aliases when they are intentional public APIs.
  Omit empty `__all__` assignments and internal helpers.
- Package initializers re-export classes, not functions or variables.

## Organization and implementation

Within classes, order `__init__`, other builtins, public properties, public
methods, private properties, and private methods. Within each group, order ordinary,
class, and static methods, then alphabetize. Modules group public before private
functions, ordinary before decorated functions, then alphabetize.

- Use f-strings and explicit `if`/`else` statements. Provide reconstructible
  `__repr__` implementations where practical.
- Keep straightforward single-use logic inline. Extract helpers for reuse,
  independent operations, or meaningful testability; do not add forwarding methods
  or predicates solely to name a short expression.
- Use one-line block comments above nontrivial continuous steps when helpful,
  without a final period.
- When renaming APIs, modules, commands, or options, update callers, documentation,
  and tests together. Never retain compatibility shims, deprecated aliases, or
  forwarding modules for old APIs or import paths; remove obsolete interfaces.

## Names and types

- Use `snake_case` and leading underscores for internals. Prefer `pathlib.Path`.
  Path values end in `_path` (`file_path`, `dir_path`); small path-focused helpers
  may use `path`/`paths`. Names and stems use `_name` and `_stem`.
- CLI-facing names may use `infile`/`outfile`; use `dest=...` when parsed names
  should identify Python path objects.
- Annotate function and method signatures. Omit return annotations for callables
  that always return `None`.
- Use `object` for values that must be inspected or narrowed, and `Any` for
  intentional unchecked passthrough. Prefer concrete types, protocols, aliases,
  and `TypedDict` when a value's shape is known.
- Type variadic arguments intentionally: use `Any` for ignored/passthrough values,
  `Unpack[...]` for known keyword shapes, or a narrower shared value type.

## Errors, logging, and CLI

- Use existing domain exceptions for user-facing failures and built-in exceptions
  for generic validation, low-level helpers, and programming errors. Shared
  exceptions live in `pipescaler.common.exceptions`.
- Preserve exception context with `raise ... from exc`.
- Use module logging for diagnostics. CLI tools may write intentional command
  output to stdout. Preserve the local logging convention when editing a module.
- Use `get_arg_groups_by_name(...)` for argument groups: positional, input,
  operation, output, additional arguments, then additional help. Omit empty groups.
- Use `type=` validators, including `enum_arg(...)`, so CLI implementations receive
  their expected types. Prefer explicit keyword-only `_main` parameters for leaf
  commands; dispatching commands may forward keyword arguments.

## Tests and documentation

- Test modules do not need package markers for discovery. Keep markers needed for
  intentional shared imports, such as `test/__init__.py`.
- Use the configured pytest import path and shared test helpers; do not add new
  `sys.path` mutations in tests.
- Follow [Documentation](DOCUMENTATION.md) for coverage, docstring sections,
  formatting, and exemptions.
- The [style tests](../test/style/) enforce docstring structure, string
  interpolation, and variadic annotation rules.

The [style audit](../skills/audit-style/SKILL.md) provides advisory checks for
export membership, definition ordering, and description capitalization. Its
coverage and manual judgment boundaries are documented in the audit skill; a
report without notes does not certify full compliance with these guides.
