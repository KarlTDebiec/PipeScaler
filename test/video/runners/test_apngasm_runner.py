#!/usr/bin/env python
#  Copyright 2020-2023 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Tests for ApngasmRunner."""
from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from pipescaler.common import ExecutableNotFoundError, get_temp_file_path
from pipescaler.image.operators.processors import XbrzProcessor
from pipescaler.testing import (
    parametrized_fixture,
    xfail_if_platform,
    get_test_infile_path,
)
from pipescaler.video.runners import ApngasmRunner


@parametrized_fixture(
    cls=ApngasmRunner,
    params=[
        {},
    ],
)
def runner(request) -> ApngasmRunner:
    return ApngasmRunner(**request.param)


@parametrized_fixture(
    cls=XbrzProcessor,
    params=[
        {"scale": 2},
    ],
)
def processor(request) -> XbrzProcessor:
    return XbrzProcessor(**request.param)


@pytest.mark.parametrize(
    ("infile"),
    [
        xfail_if_platform({"Linux", "Windows"}, ExecutableNotFoundError)("RGB"),
    ],
)
def test(infile_name: [str], runner: ApngasmRunner, processor: XbrzProcessor) -> None:
    input_path = get_test_infile_path(infile_name)

    with get_temp_file_path(".png") as two_x_path:
        two_x_image = processor(input_path)
        two_x_image.save(two_x_path)

        with get_temp_file_path(".png") as four_x_path:
            four_x_image = processor(two_x_path)
            four_x_image.save(four_x_path)

            with get_temp_file_path(".png") as output_path:
                runner.run(input_path, output_path)

                with Image.open(input_path) as input_image:
                    with Image.open(output_path) as output_image:
                        assert output_image.mode in (input_image.mode, "P")
                        assert output_image.size == input_image.size
