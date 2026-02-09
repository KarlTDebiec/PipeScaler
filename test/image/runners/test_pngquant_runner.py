#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for PngquantRunner."""

from __future__ import annotations

from os.path import getsize

import pytest
from PIL import Image

from pipescaler.common import ExecutableNotFoundError
from pipescaler.common.file import get_temp_file_path
from pipescaler.image.runners import PngquantRunner
from pipescaler.testing.file import get_test_input_path
from pipescaler.testing.fixture import parametrized_fixture
from pipescaler.testing.mark import xfail_if_platform


@parametrized_fixture(
    cls=PngquantRunner,
    params=[
        {},
    ],
)
def runner(request) -> PngquantRunner:
    """Pytest fixture that provides a PngquantRunner instance.

    Arguments:
        request: Pytest request fixture containing parameters
    Returns:
        Configured PngquantRunner instance
    """
    return PngquantRunner(**request.param)


@pytest.mark.parametrize(
    "input_filename",
    [
        xfail_if_platform({"Windows"}, ExecutableNotFoundError)("RGB"),
    ],
)
def test(input_filename: str, runner: PngquantRunner):
    """Test PngquantRunner compressing PNG images.

    Arguments:
        input_filename: Input image filename
        runner: PngquantRunner fixture instance
    """
    input_path = get_test_input_path(input_filename)

    with get_temp_file_path(".png") as output_path:
        runner.run(input_path, output_path)

        with Image.open(input_path) as input_img:
            with Image.open(output_path) as output_img:
                assert output_img.mode in (input_img.mode, "P")
                assert output_img.size == input_img.size
                assert getsize(output_path) <= getsize(input_path)


def test_repr_round_trip():
    """Test PngquantRunner repr round-trip recreation."""
    runner = PngquantRunner(arguments="--quality 1-10", timeout=1)
    recreated = eval(repr(runner))
    assert recreated.arguments == runner.arguments
    assert recreated.timeout == runner.timeout
