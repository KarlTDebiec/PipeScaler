#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for SolidColorProcessor."""

from __future__ import annotations

import pytest
from PIL import Image

from pipescaler.image.operators.processors import SolidColorProcessor
from pipescaler.image.testing import get_expected_output_mode
from pipescaler.testing.file import get_test_input_path
from pipescaler.testing.fixture import parametrized_fixture


@parametrized_fixture(
    cls=SolidColorProcessor,
    params=[
        {},
    ],
)
def processor(request: pytest.FixtureRequest) -> SolidColorProcessor:
    """Pytest fixture that provides a SolidColorProcessor instance.

    Arguments:
        request: Pytest request fixture containing parameters
    Returns:
        Configured SolidColorProcessor instance
    """
    return SolidColorProcessor(**request.param)


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
def test(input_filename: str, processor: SolidColorProcessor):
    """Test SolidColorProcessor with various image modes.

    Arguments:
        input_filename: Input image filename
        processor: SolidColorProcessor fixture instance
    """
    input_path = get_test_input_path(input_filename)
    input_img = Image.open(input_path)
    output_img = processor(input_img)

    assert output_img.mode == get_expected_output_mode(input_img)
    assert output_img.size == input_img.size
    assert len(output_img.getcolors()) == 1


@pytest.mark.parametrize("mode", ["L", "RGBA"])
def test_solid_color_averages_channels_and_scales(mode: str):
    """Fill the scaled output with each channel's mean, including alpha.

    Arguments:
        mode: grayscale or multichannel image mode
    """
    image = Image.new("RGBA", (2, 1))
    image.putpixel((0, 0), (20, 40, 60, 80))
    image.putpixel((1, 0), (100, 120, 140, 160))
    if mode == "L":
        image = Image.new("L", (2, 1))
        image.putdata([20, 100])
        expected_color = 60
    else:
        expected_color = (60, 80, 100, 120)

    output_image = SolidColorProcessor(scale=2)(image)

    assert output_image.mode == mode
    assert output_image.size == (4, 2)
    assert output_image.getcolors() == [(8, expected_color)]
