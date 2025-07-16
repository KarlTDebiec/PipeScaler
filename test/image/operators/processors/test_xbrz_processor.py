#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for XbrzProcessor."""
import pytest
from PIL import Image

from pipescaler.image.operators.processors import XbrzProcessor
from pipescaler.image.testing import get_expected_output_mode
from pipescaler.testing.file import get_test_infile_path
from pipescaler.testing.fixture import parametrized_fixture


@parametrized_fixture(
    cls=XbrzProcessor,
    params=[
        {"scale": 2},
    ],
)
def processor(request) -> XbrzProcessor:
    return XbrzProcessor(**request.param)


@pytest.mark.parametrize(
    "infile",
    [
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
def test(infile: str, processor: XbrzProcessor) -> None:
    input_path = get_test_infile_path(infile)
    input_image = Image.open(input_path)
    output_image = processor(input_image)

    assert output_image.mode in processor.outputs()["output"]
    assert output_image.mode == get_expected_output_mode(input_image)
    assert output_image.size == (
        input_image.size[0] * processor.scale,
        input_image.size[1] * processor.scale,
    )
