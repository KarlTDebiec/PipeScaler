#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for processor command-line interfaces."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from inspect import getfile
from io import StringIO
from os import getenv
from pathlib import Path

import pytest

from pipescaler.common import CommandLineInterface
from pipescaler.common.file import get_temp_file_path
from pipescaler.common.testing import run_cli_with_args
from pipescaler.image.cli import ImageProcessorsCli
from pipescaler.image.cli.processors import (
    CropCli,
    EsrganCli,
    ExpandCli,
    HeightToNormalCli,
    ModeCli,
    ResizeCli,
    SharpenCli,
    SolidColorCli,
    ThresholdCli,
    WaifuCli,
    XbrzCli,
)
from pipescaler.testing.file import get_test_infile_path, get_test_model_infile_path
from pipescaler.testing.mark import skip_if_ci, skip_if_codex

if getenv("CODEX_ENV_PYTHON_VERSION") is None:
    esrgan_path = get_test_model_infile_path("ESRGAN/1x_BC1-smooth2")
    waifu_path = get_test_model_infile_path("WaifuUpConv7/a-2-3")
else:
    esrgan_path = None
    waifu_path = None


@pytest.mark.parametrize(
    ("cli", "args", "infile"),
    [
        (CropCli, "--pixels 4 4 4 4", "RGB"),
        skip_if_codex(skip_if_ci())(
            EsrganCli,
            f"--model {esrgan_path}",
            "RGB",
        ),
        (ExpandCli, "--pixels 8 8 8 8", "RGB"),
        (HeightToNormalCli, "--sigma 1.0", "L"),
        (ModeCli, "--mode L", "RGB"),
        (ResizeCli, "--scale 2", "RGB"),
        (SharpenCli, "", "RGB"),
        (SolidColorCli, "--scale 2", "RGB"),
        (ThresholdCli, "--threshold 64 --denoise", "L"),
        skip_if_codex(skip_if_ci())(
            WaifuCli,
            f"--model {waifu_path}",
            "RGB",
        ),
        (XbrzCli, "--scale 2", "RGB"),
    ],
)
def test(cli: type[CommandLineInterface], args: str, infile: str) -> None:
    input_path = get_test_infile_path(infile)

    with get_temp_file_path(".png") as output_path:
        run_cli_with_args(cli, f"{args} {input_path} {output_path}")


@pytest.mark.parametrize(
    "commands",
    [
        (CropCli,),
        (EsrganCli,),
        (ExpandCli,),
        (HeightToNormalCli,),
        (ModeCli,),
        (ResizeCli,),
        (SharpenCli,),
        (SolidColorCli,),
        (ThresholdCli,),
        (WaifuCli,),
        (XbrzCli,),
        (ImageProcessorsCli,),
        (ImageProcessorsCli, CropCli),
        (ImageProcessorsCli, EsrganCli),
        (ImageProcessorsCli, ExpandCli),
        (ImageProcessorsCli, HeightToNormalCli),
        (ImageProcessorsCli, ModeCli),
        (ImageProcessorsCli, ResizeCli),
        (ImageProcessorsCli, SharpenCli),
        (ImageProcessorsCli, SolidColorCli),
        (ImageProcessorsCli, ThresholdCli),
        (ImageProcessorsCli, WaifuCli),
        (ImageProcessorsCli, XbrzCli),
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
        (CropCli,),
        (EsrganCli,),
        (ExpandCli,),
        (HeightToNormalCli,),
        (ModeCli,),
        (ResizeCli,),
        (SharpenCli,),
        (SolidColorCli,),
        (ThresholdCli,),
        (WaifuCli,),
        (XbrzCli,),
        (ImageProcessorsCli,),
        (ImageProcessorsCli, CropCli),
        (ImageProcessorsCli, EsrganCli),
        (ImageProcessorsCli, ExpandCli),
        (ImageProcessorsCli, HeightToNormalCli),
        (ImageProcessorsCli, ModeCli),
        (ImageProcessorsCli, ResizeCli),
        (ImageProcessorsCli, SharpenCli),
        (ImageProcessorsCli, SolidColorCli),
        (ImageProcessorsCli, ThresholdCli),
        (ImageProcessorsCli, WaifuCli),
        (ImageProcessorsCli, XbrzCli),
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
