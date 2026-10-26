# Architecture

PipeScaler processes collections of image and video files through composable
pipelines. This guide owns stable package boundaries and behavioral contracts.
Source code owns detailed API and command inventories.

## Package hierarchy

The hierarchy in [`pipescaler/__init__.py`](../pipescaler/__init__.py) declares
dependencies between top-level packages. Each nested package's `__init__.py`
declares dependency levels between its direct children.

Each child appears once. Entries separated by `/` are independent peers; children
may depend on children at earlier levels. Sibling dependency cycles are prohibited.
Hierarchy levels express architectural policy. Adding or removing an import does
not by itself authorize changing those levels; explain intentional hierarchy
changes during review.

The [architecture tests](../test/test_module_hierarchy.py) enforce declarations,
dependency direction, import style, and cycle detection. The
[hierarchy audit](../skills/audit-module-hierarchy/SKILL.md) reports inferred
minimum levels as review evidence, not automatic replacements for policy.

## Responsibilities

This table is alphabetical; dependency order belongs in the hierarchy declarations.

| Package | Responsibility |
| --- | --- |
| `cli` | Root command dispatch and user-facing adapters |
| `common` | General-purpose standard-library utilities, independent of other PipeScaler packages |
| `core` | Generic pipeline primitives, runner contracts, and shared CLI bases |
| `image` | Image pipeline types, operators, sorters, sources, termini, and external-tool adapters |
| `pipelines` | Concrete generic checkpoint and sorting helpers |
| `testing` | Reusable test fixtures, markers, paths, and execution helpers |
| `utilities` | File-scanning and related collection utilities |
| `video` | Video pipeline types, sorters, sources, termini, and external-tool adapters |

Domain packages build on `common` and `core` according to the declared hierarchy.
Concrete components depend on their abstractions; peer components may be composed
when the hierarchy permits it. Production modules do not import `test/`.
Internal imports expose their concrete dependencies as described in
[Code Style](STYLE.md).

## Pipeline contracts

- `PipeObject` tracks an input/output path, display name, parent objects, and
  relative location.
- `Segment` transforms pipeline objects and returns a tuple of pipeline objects.
  Sources create objects; sorters route them; termini collect or write outputs.
- Image processors, splitters, and mergers operate on in-memory images. File
  traversal and checkpoint orchestration belong in pipeline components.
- Checkpoint managers own checkpoint identity, freshness checks, loading, and
  saving. Preserve input lineage and path/mtime behavior when changing resume logic.
- Runners own subprocess invocation, platform assumptions, output validation, and
  model execution. Use existing image and video libraries where practical.

## CLI and test boundaries

The console entry point is declared in [`pyproject.toml`](../pyproject.toml).
CLI classes own their `argparse` command trees and help, validate inputs, and
delegate processing to lower-level components. Keep library code independent of
CLI adapters and process arguments.

`test/` mirrors the package layout. Shared assertions belong in `test/helpers.py`;
portable subprocess cases belong in `test/common/subprocess_cases.py`. Pytest's
configured root import path supports execution from the root or `test/` without
adding per-test `sys.path` changes. Preserve serial, platform, external-tool, and
large-resource markers when modifying tests.
