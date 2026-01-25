#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for ResizeProcessor."""

import pytest
from PIL import Image

from pipescaler.image.operators.processors import ResizeProcessor
from pipescaler.testing.file import get_test_input_path
from pipescaler.testing.fixture import parametrized_fixture


@parametrized_fixture(
    cls=ResizeProcessor,
    params=[
        {"scale": 2},
    ],
)
def processor(request) -> ResizeProcessor:
    """Pytest fixture that provides a ResizeProcessor instance.

    Arguments:
        request: Pytest request fixture containing parameters
    Returns:
        Configured ResizeProcessor instance
    """
    return ResizeProcessor(**request.param)


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
def test(input_filename: str, processor: ResizeProcessor):
    """Test ResizeProcessor with various image modes.

    Arguments:
        input_filename: Input image filename
        processor: ResizeProcessor fixture instance
    """
    input_path = get_test_input_path(input_filename)
    input_img = Image.open(input_path)
    output_img = processor(input_img)

    assert output_img.mode == input_img.mode
    assert output_img.size == (
        input_img.size[0] * processor.scale,
        input_img.size[1] * processor.scale,
    )
