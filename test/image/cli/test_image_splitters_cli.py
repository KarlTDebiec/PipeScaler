#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for splitter command-line interfaces."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from inspect import getfile
from io import StringIO
from pathlib import Path

import pytest

from pipescaler.common import CommandLineInterface
from pipescaler.common.file import get_temp_file_path
from pipescaler.common.testing import run_cli_with_args
from pipescaler.image.cli import ImageSplittersCli
from pipescaler.image.cli.splitters import AlphaSplitterCli
from pipescaler.testing.file import get_test_input_path


@pytest.mark.parametrize(
    ("cli", "args", "input_filename"),
    [
        (AlphaSplitterCli, "", "RGBA"),
    ],
)
def test(cli: type[CommandLineInterface], args: str, input_filename: str):
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
