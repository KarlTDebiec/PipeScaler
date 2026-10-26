# Common Utilities

`pipescaler.common` holds reusable utilities that depend only on the standard library
and other common modules. Image and video behavior belongs in the corresponding
domain packages.

## Modules and imports

| Module | Purpose |
| --- | --- |
| `argument_parsing` | Argparse validators, enum choices, duration arguments, and argument groups |
| `cli` | `CommandLineInterface` and the opt-in `ListAllCommandsAction` |
| `command_line_interface` | CLI base class, explicit argument parsing, and logging options |
| `csv` | Comma-separated string and integer lists |
| `described_enum` | `DescribedEnum`, whose members have a code and description |
| `duration` | Convert a duration string into `datetime.timedelta` |
| `exceptions` | Canonical shared exception classes |
| `file` | Temporary paths, atomic text writes, and output backups |
| `logs` | Console logging configuration and verbosity |
| `subprocess` | Captured or live subprocess output, working directories, and environments |
| `testing` | Portable echo commands and CLI invocation helpers |
| `validation` | Numeric, string, executable, path, and processing-range validation |

The original `pipescaler.common.exception` module re-exports the same classes as
`pipescaler.common.exceptions`. Existing exception handlers continue to catch the
canonical classes. `CommandLineInterface` remains available from `pipescaler.common`,
`pipescaler.common.command_line_interface`, and `pipescaler.common.cli`.
The empty `CLIKwargs` type remains available at its original import locations for
compatibility; CLI implementations may annotate their own parsed arguments.

## Argument and path validation

Use the functions in `validation` directly in Python. Argparse wrappers in
`argument_parsing` convert validation errors into `ArgumentTypeError` for CLI feedback.
Path validators accept strings and `os.PathLike[str]` objects, expand environment
variables and `~`, and return resolved absolute paths. Iterable inputs produce lists;
a string is treated as one path.

- `val_input_path` requires a file; `val_input_dir_path` requires a directory.
- `val_input_file_or_dir_path` accepts either kind of existing path.
- `val_output_path` creates missing parent directories by default and rejects an
  existing file unless `exist_ok=True`.
- `val_output_dir_path` creates a missing directory by default. `create=False`
  validates the proposed location without creating it.
- `val_child_path` accepts one filename and resolves it within its parent. It rejects
  path separators, traversal, and symlinks that resolve outside that parent. It does
  not create the child or require it to exist.
- `val_index_range` returns a zero-based range with an inclusive start and exclusive
  stop; an omitted stop uses the item count.

`input_file_arg(allow_stdin=True)` accepts `"-"` as a string sentinel; the caller must
read stdin itself. `named_input_file_arg()` parses `NAME=PATH` into a trimmed name and
a validated file path.

`parse_duration` accepts a nonnegative integer and one unit, such as `"12h"`,
`"30 days"`, or `"5 min"`. Units are seconds, minutes, hours, days, and weeks,
case-insensitively. Fractional and combined forms such as `"1.5h"` and `"1h30m"`
are rejected. `duration_arg` provides the argparse equivalent.

## Atomic text output

`open_atomic_text_file` writes a temporary sibling of the destination, flushes and
synchronizes it, and replaces the destination after a successful context exit.
The parent directory must already exist. On failure, it removes the temporary file
and leaves an existing destination untouched.

```python
from pathlib import Path

from pipescaler.common.file import open_atomic_text_file

output_path = Path("output/summary.txt")
output_path.parent.mkdir(parents=True, exist_ok=True)
with open_atomic_text_file(output_path) as output_file:
    output_file.write("Processing complete\n")
```

## Subprocesses

Both subprocess helpers take an argument list without invoking a shell and return
`(exitcode, stdout, stderr)`. Output is decoded as UTF-8 with ISO-8859-1 fallback.
The default accepted exit code is zero. `cwd_path=None` and `env=None` inherit the
current directory and environment. An explicit `env` mapping replaces the child
environment; copy `os.environ` first when adding variables to the inherited values.

`run_command` defaults to a 600-second communication timeout. On timeout it kills
the child, collects remaining output, and checks the resulting exit code. It does
not propagate `TimeoutExpired`; an unaccepted exit code raises `ValueError`.

`run_command_live` defaults to an 86400-second deadline for process exit and stream
readers to finish; `timeout=None` disables it. It logs records from both streams at
INFO level and also returns their captured text. On timeout it kills the child and
raises `subprocess.TimeoutExpired`, with captured text in `output` and `stderr`.

## CLI behavior and tests

`CommandLineInterface.main()` parses process arguments; pass an explicit sequence
such as `main(["-h"])` to supply tokens without a program name. Default console
verbosity is warnings and errors; `-v` adds INFO, `-vv` adds DEBUG, and `-q` selects
errors only. `--log-file` accepts a path or generates a timestamped name when used
without a value. Log files use UTF-8.

`ListAllCommandsAction` formats a CLI's `subcommands()` hierarchy. Applications must
register the action with their argument parser to expose a listing option; importing
the helper does not add a new PipeScaler command-line flag.

Run tests from either directory:

```sh
uv run pytest
```

```sh
cd test
uv run pytest
```

The shared common tests use `echo_command` to avoid relying on a shell's `echo`
builtin. Symlink tests skip when Windows does not grant the necessary privilege.
