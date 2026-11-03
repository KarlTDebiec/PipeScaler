# CLI extensions

An installed package can add commands to `pipescaler` by declaring Python entry
points. Each entry point names a command and identifies the class that implements
it. Install the package in the same Python environment as PipeScaler; its commands
then appear alongside the built-in commands.

## Supported locations

| Entry-point group | Command location | Required base class |
| --- | --- | --- |
| `pipescaler.cli.commands` | `pipescaler <command>` | `CommandLineInterface` |
| `pipescaler.cli.image.processors` | `pipescaler image process <command>` | `ImageProcessorCli` |
| `pipescaler.cli.image.mergers` | `pipescaler image merge <command>` | `ImageMergerCli` |
| `pipescaler.cli.image.splitters` | `pipescaler image split <command>` | `ImageSplitterCli` |

Import `CommandLineInterface` from `pipescaler.common.cli` and the image CLI bases
from `pipescaler.image.core.cli`. Image commands implement the corresponding
`processor()`, `merger()`, or `splitter()` method. Root commands can also contain
subcommands; see [Command groups](#command-groups).

## Example package

This package adds `pipescaler textures`, which prints an image's dimensions.
Create these files:

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
from pipescaler.common.cli import CommandLineInterface

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

Reinstall the package whenever you change its entry points in `pyproject.toml`,
even with an editable installation. PipeScaler reads installed package metadata;
a source directory alone does not register a command.

## Command names

An entry point refers to a concrete CLI class, rather than an instance or its
`main()` method. Its name must match the class's `name()` result. The default
removes a trailing `Cli` and lowercases the rest: `TexturesCli` becomes `textures`.
Override `name()` to choose another spelling, and use that spelling in the entry
point too.

Names must be unique within each entry-point group. An extension cannot replace
a built-in command or another extension's command.

## Command groups

An extension can group commands under a parent, such as `pipescaler textures info`.
Use `cls.subcommand_dest()` in both the parent's parser setup and its `_main`
method:

```python
# Parser construction
subparsers = parser.add_subparsers(dest=cls.subcommand_dest(), required=True)
for command in commands.values():
    command.argparser(subparsers=subparsers)

# Dispatch inside the parent's _main method
command_name = kwargs.pop(cls.subcommand_dest())
commands[command_name]._main(**kwargs)
```

Here, `commands` maps subcommand names to CLI classes. The helper gives each parent
its own internal routing key. This leaves ordinary argument names such as `domain`
and `processor` available to child commands. Do not use the helper's returned key
for application data.

## Loading and errors

PipeScaler imports extension CLI classes when it builds the parser, including for
help. Keep expensive imports and optional dependencies inside execution methods
when argument definitions do not need them.

Command classes are loaded once per group and required base class in each Python
process. Help and execution reuse those classes. Restart a long-running process
after installing or removing an extension.

An invalid registration or failed import stops parser construction. The error
identifies the command, package, and entry-point group and preserves the original
exception as its cause. PipeScaler does not silently skip broken extensions.
