#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for merger command-line interfaces."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from inspect import getfile
from io import StringIO
from pathlib import Path

import pytest

from pipescaler.common import CommandLineInterface
from pipescaler.common.file import get_temp_file_path
from pipescaler.common.testing import run_cli_with_args
from pipescaler.image.cli import ImageMergersCli
from pipescaler.image.cli.mergers import AlphaMergerCli, PaletteMatchMergerCli
from pipescaler.testing.file import get_test_input_path


@pytest.mark.parametrize(
    ("cli", "args", "input_filenames"),
    [
        (AlphaMergerCli, "", ("RGB", "L")),
        (PaletteMatchMergerCli, "", ("RGB", "alt/RGB")),
        (PaletteMatchMergerCli, "--local", ("RGB", "alt/RGB")),
        (PaletteMatchMergerCli, "--local --local_range 2", ("RGB", "alt/RGB")),
    ],
)
def test(cli: type[CommandLineInterface], args: str, input_filenames: tuple[str]):
    input_paths = [
        str(get_test_input_path(input_filename)) for input_filename in input_filenames
    ]

    with get_temp_file_path(".png") as output_path:
        run_cli_with_args(cli, f"{args} {' '.join(input_paths)} {output_path}")


@pytest.mark.parametrize(
    "commands",
    [
        (AlphaMergerCli,),
        (PaletteMatchMergerCli,),
        (ImageMergersCli,),
        (ImageMergersCli, AlphaMergerCli),
        (ImageMergersCli, PaletteMatchMergerCli),
    ],
)
def test_help(commands: tuple[type[CommandLineInterface], ...]):
    subcommands = " ".join(f"{command.name()}" for command in commands[1:])

    stdout = StringIO()
    stderr = StringIO()
    try:
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                run_cli_with_args(commands[0], f"{subcommands} -h")
    except SystemExit as exc:
        assert exc.code == 0
        assert stdout.getvalue().startswith(
            f"usage: {Path(getfile(commands[0])).name} {subcommands}"
        )
        assert stderr.getvalue() == ""


@pytest.mark.parametrize(
    "commands",
    [
        (AlphaMergerCli,),
        (PaletteMatchMergerCli,),
        (ImageMergersCli,),
        (ImageMergersCli, AlphaMergerCli),
        (ImageMergersCli, PaletteMatchMergerCli),
    ],
)
def test_usage(commands: tuple[type[CommandLineInterface], ...]):
    subcommands = " ".join(f"{command.name()}" for command in commands[1:])

    stdout = StringIO()
    stderr = StringIO()
    try:
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                run_cli_with_args(commands[0], subcommands)
    except SystemExit as exc:
        assert exc.code == 2
        assert stdout.getvalue() == ""
        assert stderr.getvalue().startswith(
            f"usage: {Path(getfile(commands[0])).name} {subcommands}"
        )
