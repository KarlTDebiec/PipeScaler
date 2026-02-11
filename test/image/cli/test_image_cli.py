#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for image command-line interface."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from inspect import getfile
from io import StringIO
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from pipescaler.common.testing import run_cli_with_args
from pipescaler.image.cli import (
    ImageCli,
    ImageMergersCli,
    ImageProcessorsCli,
    ImageSplittersCli,
    ImageUtilitiesCli,
)

if TYPE_CHECKING:
    from pipescaler.common import CommandLineInterface


@pytest.mark.parametrize(
    "commands",
    [
        (ImageCli,),
        (ImageCli, ImageMergersCli),
        (ImageCli, ImageProcessorsCli),
        (ImageCli, ImageSplittersCli),
        (ImageCli, ImageUtilitiesCli),
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
        (ImageCli,),
        (ImageCli, ImageMergersCli),
        (ImageCli, ImageProcessorsCli),
        (ImageCli, ImageSplittersCli),
        (ImageCli, ImageUtilitiesCli),
    ],
)
def test_usage(commands: tuple[type[CommandLineInterface], ...]):
    """Test that running without arguments displays usage and exits with error.

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
