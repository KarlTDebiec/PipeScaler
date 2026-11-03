# WGSL style

Use pinned `wgslfmt`: four spaces, an 88-character wrapping target, and LF line
endings. Tool versions and checks are in the
[WGSL workflow](../../.github/workflows/wgsl.yml).

- Preserve template identifiers such as `WGX` and `WGY`.
- Keep bindings, buffer layouts, and parameters synchronized with Python consumers.
- Use `//` comments to explain shader purpose, units, ranges, and non-obvious math.
