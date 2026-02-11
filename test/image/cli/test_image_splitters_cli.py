#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for splitter command-line interfaces."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from inspect import getfile
from io import StringIO
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from pipescaler.common.file import get_temp_file_path
from pipescaler.common.testing import run_cli_with_args
from pipescaler.image.cli import ImageSplittersCli
from pipescaler.image.cli.splitters import AlphaSplitterCli
from pipescaler.testing.file import get_test_input_path

if TYPE_CHECKING:
    from pipescaler.common import CommandLineInterface


@pytest.mark.parametrize(
    ("cli", "args", "input_filename"),
    [
        (AlphaSplitterCli, "", "RGBA"),
    ],
)
def test(cli: type[CommandLineInterface], args: str, input_filename: str):
    """Test splitter CLI with various input files and arguments.

    Arguments:
        cli: The command-line interface class to test
        args: Command-line arguments string
        input_filename: Input image filename
    """
    input_path = get_test_input_path(input_filename)

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
def test_help(commands: tuple[type[CommandLineInterface], ...]):
    """Test that help flag displays usage information and exits successfully.

    Arguments:
        commands: Tuple of command-line interface classes to test
    """
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
        (AlphaSplitterCli,),
        (ImageSplittersCli,),
        (ImageSplittersCli, AlphaSplitterCli),
    ],
)
def test_usage(commands: tuple[type[CommandLineInterface], ...]):
    """Test that missing arguments displays usage information and exits with error.

    Arguments:
        commands: Tuple of command-line interface classes to test
    """
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
