#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for processor command-line interfaces."""
from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from inspect import getfile
from io import StringIO
from pathlib import Path
from typing import Type

import pytest

from pipescaler.common import CommandLineInterface
from pipescaler.common.file import get_temp_file_path
from pipescaler.common.testing import run_cli_with_args
from pipescaler.image.cli import ImageUtilitiesCli
from pipescaler.image.cli.utilities import EsrganSerializerCli, WaifuSerializerCli
from pipescaler.testing.file import get_test_model_infile_path
from pipescaler.testing.mark import skip_if_ci


@pytest.mark.parametrize(
    ("cli", "args", "infile"),
    [
        skip_if_ci()(
            EsrganSerializerCli,
            "",
            "ESRGAN/1x_BC1-smooth2",
        ),
        skip_if_ci()(
            WaifuSerializerCli,
            "upconv7",
            "WaifuUpConv7/a-2-1.json",
        ),
    ],
)
def test(cli: Type[CommandLineInterface], args: str, infile: str) -> None:
    input_path = get_test_model_infile_path(infile)

    with get_temp_file_path(".pth") as output_path:
        run_cli_with_args(cli, f"{args} {input_path} {output_path}")


@pytest.mark.parametrize(
    "commands",
    [
        (EsrganSerializerCli,),
        (WaifuSerializerCli,),
        (ImageUtilitiesCli,),
        (ImageUtilitiesCli, EsrganSerializerCli),
        (ImageUtilitiesCli, WaifuSerializerCli),
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
        (EsrganSerializerCli,),
        (WaifuSerializerCli,),
        (ImageUtilitiesCli,),
        (ImageUtilitiesCli, EsrganSerializerCli),
        (ImageUtilitiesCli, WaifuSerializerCli),
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
