#!/usr/bin/env python
#  Copyright 2020-2023 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Tests for processor command-line interfaces."""
from __future__ import annotations

from typing import Type

from pytest import mark

from pipescaler.common import CommandLineInterface, get_temp_file_path
from pipescaler.image.cli import ImageUtilitiesCli
from pipescaler.image.cli.utilities import EsrganSerializerCli, WaifuSerializerCli
from pipescaler.testing import (
    get_test_model_infile_path,
    run_cli_with_args,
    skip_if_ci,
    xfail_system_exit,
)


@mark.parametrize(
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


@mark.parametrize(
    ("cli", "args"),
    [
        xfail_system_exit()(ImageUtilitiesCli, ""),
        xfail_system_exit()(EsrganSerializerCli, "-h"),
        xfail_system_exit()(WaifuSerializerCli, ""),
        xfail_system_exit()(WaifuSerializerCli, "-h"),
        xfail_system_exit()(ImageUtilitiesCli, ""),
        xfail_system_exit()(ImageUtilitiesCli, "-h"),
        xfail_system_exit()(ImageUtilitiesCli, "esrgan-serializer"),
        xfail_system_exit()(ImageUtilitiesCli, "esrganserializer -h"),
        xfail_system_exit()(ImageUtilitiesCli, "waifu-serializer"),
        xfail_system_exit()(ImageUtilitiesCli, "waifuserializer -h"),
    ],
)
def test_help(cli: Type[CommandLineInterface], args: str) -> None:
    run_cli_with_args(cli, f"{args}")
