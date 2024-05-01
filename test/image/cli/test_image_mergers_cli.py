#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for merger command-line interfaces."""
from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from inspect import getfile
from io import StringIO
from pathlib import Path
from typing import Type

import pytest

from pipescaler.common import (
    CommandLineInterface,
    get_temp_file_path,
    run_cli_with_args,
)
from pipescaler.image.cli import ImageMergersCli
from pipescaler.image.cli.mergers import AlphaMergerCli
from pipescaler.testing import (
    get_test_infile_path,
)


@pytest.mark.parametrize(
    ("cli", "args", "infiles"),
    [
        (AlphaMergerCli, "", ("RGB", "L")),
    ],
)
def test(cli: Type[CommandLineInterface], args: str, infiles: tuple[str]) -> None:
    input_paths = [str(get_test_infile_path(infile)) for infile in infiles]

    with get_temp_file_path(".png") as output_path:
        run_cli_with_args(cli, f"{args} {' '.join(input_paths)} {output_path}")


@pytest.mark.parametrize(
    "commands",
    [
        (AlphaMergerCli,),
        (ImageMergersCli,),
        (ImageMergersCli, AlphaMergerCli),
    ],
)
def test_help(commands: tuple[Type[CommandLineInterface], ...]) -> None:
    subcommands = " ".join(f"{command.name()}" for command in commands[1:])

    stdout = StringIO()
    stderr = StringIO()
    try:
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                run_cli_with_args(commands[0], f"{subcommands} -h")
    except SystemExit as error:
        assert error.code == 0
        assert stdout.getvalue().startswith(
            f"usage: {Path(getfile(commands[0])).name} {subcommands}"
        )
        assert stderr.getvalue() == ""


@pytest.mark.parametrize(
    "commands",
    [
        (AlphaMergerCli,),
        (ImageMergersCli,),
        (ImageMergersCli, AlphaMergerCli),
    ],
)
def test_usage(commands: tuple[Type[CommandLineInterface], ...]):
    subcommands = " ".join(f"{command.name()}" for command in commands[1:])

    stdout = StringIO()
    stderr = StringIO()
    try:
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                run_cli_with_args(commands[0], subcommands)
    except SystemExit as error:
        assert error.code == 2
        assert stdout.getvalue() == ""
        assert stderr.getvalue().startswith(
            f"usage: {Path(getfile(commands[0])).name} {subcommands}"
        )
