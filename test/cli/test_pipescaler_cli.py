#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for PipeScaler command-line interface."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from inspect import getfile
from io import StringIO
from pathlib import Path

import pytest

from pipescaler.cli import PipeScalerCli
from pipescaler.common import CommandLineInterface
from pipescaler.common.testing import run_cli_with_args
from pipescaler.image.cli import ImageCli
from pipescaler.testing.mark import parametrize_with_readable_ids


@parametrize_with_readable_ids(
    "commands",
    [
        (PipeScalerCli,),
        (PipeScalerCli, ImageCli),
    ],
)
def test_help(commands: tuple[type[CommandLineInterface], ...]) -> None:
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
        (PipeScalerCli,),
        (PipeScalerCli, ImageCli),
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
    except SystemExit as error:
        assert error.code == 2
        assert stdout.getvalue() == ""
        assert stderr.getvalue().startswith(
            f"usage: {Path(getfile(commands[0])).name} {subcommands}"
        )
