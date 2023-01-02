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
def test(cli: Type[CommandLineInterface], args: str, infile: str) -> None:
    input_path = get_test_infile_path(infile)

    with get_temp_file_path(".png") as output_path:
        run_cli_with_args(cli, f"{args} {input_path} {output_path}")


@mark.parametrize(
    ("cli", "args"),
    [
        xfail_system_exit()(CropCli, "-h"),
        xfail_system_exit()(EsrganCli, "-h"),
        xfail_system_exit()(ExpandCli, "-h"),
        xfail_system_exit()(HeightToNormalCli, "-h"),
        xfail_system_exit()(ModeCli, "-h"),
        xfail_system_exit()(ResizeCli, "-h"),
        xfail_system_exit()(SharpenCli, "-h"),
        xfail_system_exit()(SolidColorCli, "-h"),
        xfail_system_exit()(ThresholdCli, "-h"),
        xfail_system_exit()(WaifuCli, "-h"),
        xfail_system_exit()(XbrzCli, "-h"),
        xfail_system_exit()(ImageProcessorsCli, "-h"),
        xfail_system_exit()(ImageProcessorsCli, "crop -h"),
        xfail_system_exit()(ImageProcessorsCli, "esrgan -h"),
        xfail_system_exit()(ImageProcessorsCli, "expand -h"),
        xfail_system_exit()(ImageProcessorsCli, "heighttonormal -h"),
        xfail_system_exit()(ImageProcessorsCli, "mode -h"),
        xfail_system_exit()(ImageProcessorsCli, "resize -h"),
        xfail_system_exit()(ImageProcessorsCli, "sharpen -h"),
        xfail_system_exit()(ImageProcessorsCli, "solidcolor -h"),
        xfail_system_exit()(ImageProcessorsCli, "threshold -h"),
        xfail_system_exit()(ImageProcessorsCli, "waifu -h"),
        xfail_system_exit()(ImageProcessorsCli, "xbrz -h"),
    ],
)
def test_help(cli: Type[CommandLineInterface], args: str):
    run_cli_with_args(ImageProcessorsCli, f"{args}")
