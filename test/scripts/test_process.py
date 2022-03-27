#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for ProcessCommandLineTool."""
from __future__ import annotations

from inspect import getfile

from pytest import fixture, mark

from pipescaler.common import run_command, temporary_filename
from pipescaler.scripts.process_command_line_tool import ProcessCommandLineTool
from pipescaler.testing import get_infile, get_model_infile, skip_if_ci


@fixture
def script(request) -> str:
    return getfile(ProcessCommandLineTool)


@mark.parametrize(
    ("infile", "args"),
    [
        ("RGB", "-h"),
        ("RGB", "crop -h"),
        ("RGB", "crop --pixels 4 4 4 4"),
        ("RGB", "esrgan -h"),
        skip_if_ci()(
            "RGB", f"esrgan --model {get_model_infile('ESRGAN/1x_BC1-smooth2')}"
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
        ("RGB", "threshold --threshold 64 --denoise"),
        ("RGB", "waifu -h"),
        skip_if_ci()("RGB", f"waifu --model {get_model_infile('WaifuUpConv7/a-2-3')}"),
        ("RGB", "web -h"),
        ("RGB", "xbrz -h"),
        ("RGB", "xbrz --scale 2"),
    ],
)
def test(script: str, infile: str, args: str) -> None:
    infile = get_infile(infile)

    with temporary_filename(".png") as outfile:
        command = f"coverage run {script} {args} {infile} {outfile}"
        run_command(command)
