#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Tests for EsrganCli."""
from __future__ import annotations

from inspect import getfile

from pytest import fixture, mark

from pipescaler.cli.processors import EsrganCli
from pipescaler.common import get_temp_file_path, run_command
from pipescaler.testing import (
    get_test_infile_path,
    get_test_model_infile_path,
    skip_if_ci,
)


@fixture
def script(request) -> str:
    return getfile(EsrganCli)


@mark.parametrize(
    ("infile", "args"),
    [
        ("RGB", "-h"),
        skip_if_ci()(
            "RGB", f"--model {get_test_model_infile_path('ESRGAN/1x_BC1-smooth2')}"
        ),
    ],
)
def test(script: str, infile: str, args: str) -> None:
    input_path = get_test_infile_path(infile)

    with get_temp_file_path(".png") as output_path:
        command = f"coverage run {script} {args} {input_path} {output_path}"
        run_command(command)
