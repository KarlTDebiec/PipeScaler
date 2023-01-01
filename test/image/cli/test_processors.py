#!/usr/bin/env python
#  Copyright 2020-2023 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Tests for processor command-line interfaces."""
from __future__ import annotations

from typing import Type

from pytest import mark

from pipescaler.common import CommandLineInterface, get_temp_file_path
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
from pipescaler.testing import (
    get_test_infile_path,
    get_test_model_infile_path,
    run_cli_with_args,
    skip_if_ci,
    xfail_system_exit,
)


@mark.parametrize(
    ("args"),
    [
        xfail_system_exit()("-h"),
        xfail_system_exit()("crop -h"),
        xfail_system_exit()("esrgan -h"),
        xfail_system_exit()("expand -h"),
        xfail_system_exit()("heighttonormal -h"),
        xfail_system_exit()("mode -h"),
        xfail_system_exit()("resize -h"),
        xfail_system_exit()("sharpen -h"),
        xfail_system_exit()("solidcolor -h"),
        xfail_system_exit()("threshold -h"),
        xfail_system_exit()("waifu -h"),
        xfail_system_exit()("xbrz -h"),
    ],
)
def test_collected(args: str):
    run_cli_with_args(ImageProcessorsCli, f"{args}")


@mark.parametrize(
    ("cli", "args", "infile"),
    [
        (CropCli, "--pixels 4 4 4 4", "RGB"),
        skip_if_ci()(
            EsrganCli,
            f"--model {get_test_model_infile_path('ESRGAN/1x_BC1-smooth2')}",
            "RGB",
        ),
        (ExpandCli, "--pixels 8 8 8 8", "RGB"),
        (HeightToNormalCli, "--sigma 1.0", "L"),
        (ModeCli, "--mode L", "RGB"),
        (ResizeCli, "--scale 2", "RGB"),
        (SharpenCli, "", "RGB"),
        (SolidColorCli, "--scale 2", "RGB"),
        (ThresholdCli, "--threshold 64 --denoise", "L"),
        skip_if_ci()(
            WaifuCli,
            f"--model {get_test_model_infile_path('WaifuUpConv7/a-2-3')}",
            "RGB",
        ),
        (XbrzCli, "--scale 2", "RGB"),
    ],
)
def test_individual(cli: Type[CommandLineInterface], args: str, infile: str) -> None:
    input_path = get_test_infile_path(infile)

    with get_temp_file_path(".png") as output_path:
        run_cli_with_args(cli, f"{args} {input_path} {output_path}")
