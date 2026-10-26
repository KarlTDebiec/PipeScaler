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
runs for that PR; each merged commit keeps its own workflow run. Describe
validation actually performed, including skipped checks and platform limitations.

## Pull requests

Keep descriptions concise. Use these sections:

```markdown
## Background

Why the change is needed.

## Changes

- What changed.

## Notes

Optional: a non-obvious choice, implementation limitation, or separate issue.
```

Write for reviewers without prior context. Each Changes bullet should identify
the affected area and its concrete result. Describe the final implementation and
omit chat history. Include relevant validation and explain material limitations
or architectural choices in Notes. Omit Notes when there is nothing to add.

Link the relevant issues. Use closing references such as `Closes #123` when the
PR resolves an issue.
