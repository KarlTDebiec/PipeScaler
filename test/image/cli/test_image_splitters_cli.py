#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for splitter command-line interfaces."""
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
from pipescaler.image.cli import ImageSplittersCli
from pipescaler.image.cli.splitters import AlphaSplitterCli
from pipescaler.testing import (
    get_test_infile_path,
)


@pytest.mark.parametrize(
    ("cli", "args", "infile"),
    [
        (AlphaSplitterCli, "", "RGBA"),
    ],
)
def test(cli: Type[CommandLineInterface], args: str, infile: str) -> None:
    input_path = get_test_infile_path(infile)

    with get_temp_file_path(".png") as output_path_1:
        with get_temp_file_path(".png") as output_path_2:
            run_cli_with_args(
                cli, f"{args} {input_path} {output_path_1} {output_path_2}"
            )


@pytest.mark.parametrize(
    "commands",
    [
        (AlphaSplitterCli,),
        (ImageSplittersCli,),
        (ImageSplittersCli, AlphaSplitterCli),
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
        (AlphaSplitterCli,),
        (ImageSplittersCli,),
        (ImageSplittersCli, AlphaSplitterCli),
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
