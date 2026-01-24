#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for ExpandProcessor."""

import pytest
from PIL import Image

from pipescaler.image.operators.processors import ExpandProcessor
from pipescaler.image.testing import get_expected_output_mode
from pipescaler.testing.file import get_test_input_path
from pipescaler.testing.fixture import parametrized_fixture


@parametrized_fixture(
    cls=ExpandProcessor,
    params=[
        {"pixels": (4, 4, 4, 4)},
    ],
)
def processor(request) -> ExpandProcessor:
    return ExpandProcessor(**request.param)


@pytest.mark.parametrize(
    "input_filename",
    [
        "1",
        "L",
        "LA",
        "RGB",
        "RGBA",
        "PL",
        "PLA",
        "PRGB",
        "PRGBA",
    ],
)
def test(input_filename: str, processor: ExpandProcessor):
    input_path = get_test_input_path(input_filename)
    input_img = Image.open(input_path)
    output_img = processor(input_img)

    assert output_img.mode == get_expected_output_mode(input_img)
    assert output_img.size == (
        input_img.size[0] + processor.left + processor.right,
        input_img.size[1] + processor.top + processor.bottom,
    )
