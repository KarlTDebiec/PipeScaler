# Documentation

Document current behavior, meaningful constraints, and reasons for non-obvious
choices. Keep each topic with its owner and link to it. Prefer source docstrings
for API contracts; avoid duplicating callable inventories or keeping work logs
in maintained documentation.

## Ownership

| Location | Content |
| --- | --- |
| `AGENTS.md` | Instructions and routing to repository guides |
| `README.md` | Project orientation and entry points |
| `docs/ARCHITECTURE.md` | Package boundaries, dependency policy, and pipeline contracts |
| `docs/STYLE.md` | Python implementation conventions |
| `__init__.py` hierarchy blocks | Dependency levels between direct package children |
| Source docstrings and CLI help | API contracts, options, units, and defaults |
| `.github/workflows/` and `pyproject.toml` | Exact CI commands, dependencies, and tool configuration |

Use relative Markdown links and check target paths and anchors, including case.
Distinguish implemented behavior from proposals and measured results from
assumptions. Update documentation with the code it describes.

## Python docstrings

- Document modules, classes, properties, named functions, internal helpers,
  setters, enums, and public type definitions.
- `@overload` stubs may use the documented implementation's contract.
- Document class attributes with a docstring immediately below each attribute.
- Use Markdown and Google-style docstrings with `Arguments:` instead of `Args:`.
  Do not use reStructuredText markup such as double backticks.
- Begin argument, return, and yield descriptions in lowercase unless the first
  word is a type name. Do not put blank lines between adjacent sections.

| Section | Requirement |
| --- | --- |
| `Arguments:` | Document parameters that need explanation; omit when there are none. |
| `Returns:` | Document returned values, including abstract contracts; omit for `None`. Properties and pytest fixtures may describe their value in the summary. |
| `Yields:` | Use for generators and context managers that yield. |
| `Raises:` | Document explicit raises and meaningful propagated exceptions. A sole abstract `raise NotImplementedError` is a contract placeholder. |
