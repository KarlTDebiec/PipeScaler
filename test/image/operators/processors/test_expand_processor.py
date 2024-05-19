#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for ExpandProcessor."""
import pytest
from PIL import Image

from pipescaler.image.operators.processors import ExpandProcessor
from pipescaler.image.testing import get_expected_output_mode
from pipescaler.testing.file import get_test_infile_path
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
    "infile",
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
def test(infile: str, processor: ExpandProcessor) -> None:
    input_path = get_test_infile_path(infile)
    input_image = Image.open(input_path)
    output_image = processor(input_image)

    assert output_image.mode == get_expected_output_mode(input_image)
    assert output_image.size == (
        input_image.size[0] + processor.left + processor.right,
        input_image.size[1] + processor.top + processor.bottom,
    )
