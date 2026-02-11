#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for processor command-line interfaces."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from inspect import getfile
from io import StringIO
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from pipescaler.common.file import get_temp_file_path
from pipescaler.common.testing import run_cli_with_args
from pipescaler.image.cli import ImageProcessorsCli
from pipescaler.image.cli.processors import (
    CropCli,
    ExpandCli,
    HeightToNormalCli,
    ModeCli,
    ResizeCli,
    SharpenCli,
    SolidColorCli,
    ThresholdCli,
    XbrzCli,
)
from pipescaler.testing.file import get_test_input_path

if TYPE_CHECKING:
    from pipescaler.common import CommandLineInterface


@pytest.mark.parametrize(
    ("cli", "args", "input_filename"),
    [
        (CropCli, "--pixels 4 4 4 4", "RGB"),
        (ExpandCli, "--pixels 8 8 8 8", "RGB"),
        (HeightToNormalCli, "--sigma 1.0", "L"),
        (ModeCli, "--mode L", "RGB"),
        (ResizeCli, "--scale 2", "RGB"),
        (SharpenCli, "", "RGB"),
        (SolidColorCli, "--scale 2", "RGB"),
        (ThresholdCli, "--threshold 64 --denoise", "L"),
        (XbrzCli, "--scale 2", "RGB"),
    ],
)
def test(cli: type[CommandLineInterface], args: str, input_filename: str):
    """Test processor CLI with various input files and arguments.

    Arguments:
        cli: The command-line interface class to test
        args: Command-line arguments string
        input_filename: Input image filename
    """
    input_path = get_test_input_path(input_filename)

    with get_temp_file_path(".png") as output_path:
        run_cli_with_args(cli, f"{args} {input_path} {output_path}")


@pytest.mark.parametrize(
    "commands",
    [
        (CropCli,),
        (ExpandCli,),
        (HeightToNormalCli,),
        (ModeCli,),
        (ResizeCli,),
        (SharpenCli,),
        (SolidColorCli,),
        (ThresholdCli,),
        (XbrzCli,),
        (ImageProcessorsCli,),
        (ImageProcessorsCli, CropCli),
        (ImageProcessorsCli, ExpandCli),
        (ImageProcessorsCli, HeightToNormalCli),
        (ImageProcessorsCli, ModeCli),
        (ImageProcessorsCli, ResizeCli),
        (ImageProcessorsCli, SharpenCli),
        (ImageProcessorsCli, SolidColorCli),
        (ImageProcessorsCli, ThresholdCli),
        (ImageProcessorsCli, XbrzCli),
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
        (CropCli,),
        (ExpandCli,),
        (HeightToNormalCli,),
        (ModeCli,),
        (ResizeCli,),
        (SharpenCli,),
        (SolidColorCli,),
        (ThresholdCli,),
        (XbrzCli,),
        (ImageProcessorsCli,),
        (ImageProcessorsCli, CropCli),
        (ImageProcessorsCli, ExpandCli),
        (ImageProcessorsCli, HeightToNormalCli),
        (ImageProcessorsCli, ModeCli),
        (ImageProcessorsCli, ResizeCli),
        (ImageProcessorsCli, SharpenCli),
        (ImageProcessorsCli, SolidColorCli),
        (ImageProcessorsCli, ThresholdCli),
        (ImageProcessorsCli, XbrzCli),
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
