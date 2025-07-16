#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for PngquantRunner."""

from __future__ import annotations

from os.path import getsize

import pytest
from PIL import Image

from pipescaler.common import ExecutableNotFoundError
from pipescaler.common.file import get_temp_file_path
from pipescaler.image.runners import PngquantRunner
from pipescaler.testing.file import get_test_infile_path
from pipescaler.testing.fixture import parametrized_fixture
from pipescaler.testing.mark import xfail_if_platform


@parametrized_fixture(
    cls=PngquantRunner,
    params=[
        {},
    ],
)
def runner(request) -> PngquantRunner:
    return PngquantRunner(**request.param)


@pytest.mark.parametrize(
    "infile_name",
    [
        xfail_if_platform({"Windows"}, ExecutableNotFoundError)("RGB"),
    ],
)
def test(infile_name: str, runner: PngquantRunner) -> None:
    input_path = get_test_infile_path(infile_name)

    with get_temp_file_path(".png") as output_path:
        runner.run(input_path, output_path)

        with Image.open(input_path) as input_image:
            with Image.open(output_path) as output_image:
                assert output_image.mode in (input_image.mode, "P")
                assert output_image.size == input_image.size
                assert getsize(output_path) <= getsize(input_path)
