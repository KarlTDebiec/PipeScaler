# WGSL style

Format maintained `.wgsl` sources with pinned `wgslfmt`, using four spaces and LF
line endings. Tool versions, formatter settings, and CI commands belong in the
[WGSL workflow](../../.github/workflows/wgsl.yml).

## Contracts

Preserve template identifiers such as `WGX` and `WGY` in maintained sources. The
palette shader uses 8×1 workgroups for basic matching and 8×8 for local matching;
keep these sizes synchronized with `PaletteShaderMatcher`. Validate expanded
copies of both configurations with pinned Naga.

Keep bindings, buffer layouts, and parameter meanings synchronized with their
Python consumers. Update consumers when changing these contracts.

## Documentation

Preserve copyright/license headers and purpose comments. Document buffer layouts,
units, numerical ranges, and non-obvious math beside the relevant declarations or
calculations.

Formatting and static validation require no GPU and do not establish runtime
correctness or backend compatibility.
