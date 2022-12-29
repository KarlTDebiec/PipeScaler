#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Tests for PngquantRunner."""
from os.path import getsize
from pathlib import Path

import pytest
from PIL import Image

from pipescaler.common import ExecutableNotFoundError, get_temp_file_path
from pipescaler.image.runners import PngquantRunner
from pipescaler.testing import (
    get_test_infile_path,
    parametrized_fixture,
    xfail_if_platform,
)


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
    input_path: Path = get_test_infile_path(infile)

    with get_temp_file_path(".png") as output_path:
        runner.run(input_path, output_path)

        with Image.open(input_path) as input_image:
            with Image.open(output_path) as output_image:
                assert output_image.mode in (input_image.mode, "P")
                assert output_image.size == input_image.size
                assert getsize(output_path) <= getsize(input_path)
