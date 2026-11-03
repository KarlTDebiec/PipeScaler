# CLI extensions

Separately installed packages can add commands to the `pipescaler` executable
through Python package entry points. PipeScaler discovers their CLI classes in
the same Python environment and includes them in help and execution alongside
its built-in commands.

## Supported locations

| Entry-point group | Command location | Required base class |
| --- | --- | --- |
| `pipescaler.cli.commands` | `pipescaler <command>` | `CommandLineInterface` |
| `pipescaler.cli.image.processors` | `pipescaler image process <command>` | `ImageProcessorCli` |
| `pipescaler.cli.image.mergers` | `pipescaler image merge <command>` | `ImageMergerCli` |
| `pipescaler.cli.image.splitters` | `pipescaler image split <command>` | `ImageSplitterCli` |

Import `CommandLineInterface` from `pipescaler.common.command_line_interface`.
The image CLI bases are available from `pipescaler.image.core.cli`. A root command
can define its own command subtree using the existing CLI parser conventions.
Nested commands implement the appropriate image CLI contract, including its
`processor()`, `merger()`, or `splitter()` method.

## Minimal extension package

This example registers a `textures` command that reports an image's dimensions.
Create this package layout:

```text
texture-tools/
    pyproject.toml
    texture_tools/
        __init__.py
        cli.py
```

Leave `texture_tools/__init__.py` empty. In `pyproject.toml`, declare the package,
its PipeScaler dependency, and the command entry point:

```toml
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[project]
name = "texture-tools"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = ["pipescaler"]

[project.entry-points."pipescaler.cli.commands"]
textures = "texture_tools.cli:TexturesCli"
```

In `texture_tools/cli.py`, define a concrete CLI class:

```python
from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from PIL import Image

from pipescaler.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
)
from pipescaler.common.command_line_interface import CommandLineInterface

__all__ = ["TexturesCli"]


class TexturesCli(CommandLineInterface):
    """Report texture dimensions."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add an image path to the command parser.

        Arguments:
            parser: parser receiving the input argument
        """
        super().add_arguments_to_argparser(parser)
        arg_groups = get_arg_groups_by_name(parser, "input arguments")

        # Input arguments
        arg_groups["input arguments"].add_argument(
            "input_path",
            type=input_file_arg(),
            help="texture image file",
        )

    @classmethod
    def _main(cls, *, input_path: Path):
        """Print the selected image's dimensions.

        Arguments:
            input_path: image to inspect
        """
        with Image.open(input_path) as image:
            print(f"{image.width} x {image.height}")
```

Install the extension into the environment that provides `pipescaler`, then run:

```console
uv pip install -e /path/to/texture-tools
pipescaler --help
pipescaler textures --help
pipescaler textures /path/to/image.png
```

Installation creates the distribution metadata used for discovery. Merely
placing an extension's source directory next to PipeScaler does not register it.
Reinstall the extension after changing entry points in `pyproject.toml`, including
for editable installations.

## Naming and loading

The entry-point value identifies a CLI **class**, not a class instance or its
`main()` method. The class must be concrete and inherit the base for its group.

The entry-point name must match the class's `name()` result. By default,
`CommandLineInterface.name()` removes a trailing `Cli` and lowercases the remaining
class name, so `TexturesCli` registers as `textures`. Override `name()` when a
different command spelling is needed, and use that spelling in the entry point.
Duplicate names within a group are errors, including collisions with built-in
commands. Extensions cannot replace existing commands.

PipeScaler loads extension classes while constructing the command parser. Keep
expensive or optional imports inside execution methods when they are unnecessary
for help or argument definitions. Loaded registrations are cached per group and
base class for the lifetime of the Python process; parsing and dispatch reuse the
same classes. Restart a long-running process after installing or removing an
extension.

An invalid registration or failed import stops construction of the affected
command tree with an error naming the command, distribution, and entry-point
group. Original exceptions remain chained to that error. Extensions are not
silently skipped, and discovery does not install packages or modify built-ins.
