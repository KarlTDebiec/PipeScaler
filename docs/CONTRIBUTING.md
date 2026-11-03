# Contributing

## Branches

Name branches `feature/brief-description`. Continue the existing branch when
requested. The remote is `origin`; target pull requests at `master`. Keep unrelated
working-tree changes out of commits and pull requests.

Interact with GitHub through the GitHub MCP; do not use `gh`.

## CI usage

Batch related changes, validate locally, and push when ready for review. Do not
push each small edit or use Actions as the primary edit/test loop; cancelled runs
still consume runner time. Use remote CI to confirm platform behavior and
investigate failures that cannot be reproduced locally.

Use `uv run` for repository tools and follow the
[validation guidance](../AGENTS.md#validation) before pushing. Keep tests requiring
serial execution serial.

The [workflow files](../.github/workflows/) own exact triggers, commands,
dependencies, and tool versions. Pull requests run Linux checks. Pushes to `master`
after merging run Linux, macOS, and Windows checks. New PR updates cancel older
runs for that PR; each merged commit keeps its own workflow run. GitHub checks
provide routine validation results. Mention validation gaps or platform limitations
in PR Notes only when they materially affect review.

## WGSL tooling

Install [Rust/rustup](https://rustup.rs/) and the platform's native linker/build
tools once (Visual Studio C++ Build Tools on Windows, Xcode command-line tools on
macOS, or `build-essential` on Ubuntu). Then run from the repository root:

```shell
uv run python scripts/wgsl.py install
uv run python scripts/wgsl.py format
uv run python scripts/wgsl.py format --check
uv run python scripts/wgsl.py lint
```

`install` uses the Rust version, Naga release, and full formatter commit in
[`scripts/wgsl_tools.toml`](../scripts/wgsl_tools.toml), with locked Cargo
dependencies. Binaries live in ignored `local/wgsl-tools/`; matching installations
are reused. Keep the Naga pin aligned with the compiler used by the `wgpu-native`
runtime when updating `wgpu`.

`format` and `lint` accept optional repository-relative WGSL file paths. Without
paths, they check every existing tracked `.wgsl` file. Formatting edits maintained
sources; `format --check` never writes. Validation substitutes both palette
workgroup configurations into temporary files and reports errors against the
maintained source. These static checks need no GPU; shader execution tests still
require a usable compute device.

The separate [WGSL workflow](../.github/workflows/wgsl.yml) checks PRs and pushes
to `master`. For PRs, inline change detection runs the checks for changes to WGSL
files, workflow or line-ending settings, and tool or dependency version files.
Other PR changes skip shader checks while completing the check successfully.
Failed PR diffs fail the job. Pushes to `master` always run the checks. If
formatting fails, subsequent validation and tooling tests are skipped.
The workflow caches binaries by OS, architecture, and installation pins. For its
GPU-free Python tests, only the development dependency group is installed.

To run the tooling regression tests after installing the native tools:

```shell
uv run pytest test/scripts/test_wgsl.py
```

## Pull requests

Keep descriptions concise. Use these sections:

```markdown
## Background

The current problem or constraint, stated in the present tense.

## Changes

- What the change does, stated in the present tense.

## Notes

Optional: a non-obvious choice, implementation limitation, or separate issue.
```

Write for reviewers without prior context. Use present tense in both Background
and Changes:

- Background describes the current problem or constraint: "Checkpoint writes leave
  partial files when a runner fails."
- Changes describes the resulting behavior: "Writes checkpoints to temporary files
  before replacing the destination."

Each Changes bullet identifies the affected area and its concrete result.
Describe the final implementation and omit chat history or a work log. Notes
covers non-obvious choices, material limitations, or architectural decisions;
omit Notes when there is nothing to add.

Keep routine validation out of the description. Do not list executed commands,
passing checks, test counts, or statements that tests, Ruff, ty, or CI pass.
Required checks still run; their results belong in GitHub checks. Do not add a
Testing or Validation section or append a validation checklist to Notes. Describe
new regression coverage by the behavior it protects when that helps explain the
change, rather than reporting that the tests run. Mention a validation gap only
when it leaves relevant behavior unverified and materially affects review.

Attach related issues separately from the description. Closing keywords are not
required.
