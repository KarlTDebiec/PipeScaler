#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for PngquantRunner"""
from os.path import getsize
from pathlib import Path

import pytest
from PIL import Image

from pipescaler.common import ExecutableNotFoundError, temporary_filename
from pipescaler.runners import PngquantRunner
from pipescaler.testing import get_infile, parametrized_fixture, xfail_if_platform


@parametrized_fixture(
    cls=PngquantRunner,
    params=[
        {},
    ],
)
def runner(request) -> PngquantRunner:
    return PngquantRunner(**request.param)


@pytest.mark.parametrize(
    ("infile"),
    [
        xfail_if_platform({"Windows"}, ExecutableNotFoundError)("RGB"),
    ],
)
def test(infile: str, runner: PngquantRunner) -> None:
    infile = get_infile(infile)

    with temporary_filename(".png") as outfile:
        outfile = Path(outfile)
        runner.run(infile, outfile)

        with Image.open(infile) as input_image, Image.open(outfile) as output_image:
            assert output_image.mode in (input_image.mode, "P")
            assert output_image.size == input_image.size
            assert getsize(outfile) <= getsize(infile)