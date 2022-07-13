#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Tests for ProcessorsCli."""
from __future__ import annotations

from inspect import getfile

from pytest import fixture, mark

from pipescaler.cli.processors_cli import ProcessorsCli
from pipescaler.common import get_temp_file_path, run_command
from pipescaler.testing import (
    get_test_infile_path,
    get_test_model_infile_path,
    skip_if_ci,
    xfail_value,
)


@fixture
def script(request) -> str:
    return getfile(ProcessorsCli)


@mark.parametrize(
    ("infile", "args"),
    [
        xfail_value()("RGB", ""),
        ("RGB", "-h"),
        ("RGB", "crop -h"),
        ("RGB", "crop --pixels 4 4 4 4"),
        ("RGB", "esrgan -h"),
        skip_if_ci()(
            "RGB",
            f"esrgan --model {get_test_model_infile_path('ESRGAN/1x_BC1-smooth2')}",
        ),
        ("RGB", "expand -h"),
        ("RGB", "expand --pixels 8 8 8 8"),
        ("RGB", "heighttonormal -h"),
        ("L", "heighttonormal --sigma 1.0"),
        ("RGB", "mode -h"),
        ("RGB", "mode --mode L"),
        ("RGB", "resize -h"),
        ("RGB", "resize --scale 2"),
        ("RGB", "sharpen -h"),
        ("RGB", "sharpen"),
        ("RGB", "solidcolor -h"),
        ("RGB", "solidcolor --scale 2"),
        ("RGB", "threshold -h"),
        ("L", "threshold --threshold 64 --denoise"),
        ("RGB", "waifu -h"),
        skip_if_ci()(
            "RGB", f"waifu --model {get_test_model_infile_path('WaifuUpConv7/a-2-3')}"
        ),
        ("RGB", "web -h"),
        ("RGB", "xbrz -h"),
        ("RGB", "xbrz --scale 2"),
    ],
)
def test(script: str, infile: str, args: str) -> None:
    input_path = get_test_infile_path(infile)

    with get_temp_file_path(".png") as output_path:
        command = f"coverage run {script} {args} {input_path} {output_path}"
        run_command(command)
