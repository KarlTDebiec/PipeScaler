#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for SharpenProcessor."""

from __future__ import annotations

import pytest
from PIL import Image

from pipescaler.image.operators.processors import SharpenProcessor
from pipescaler.image.testing import (
    get_expected_output_mode,
    xfail_unsupported_image_mode,
)
from pipescaler.testing.file import get_test_input_path


@pytest.fixture
def processor() -> SharpenProcessor:
    """Provide a fresh SharpenProcessor instance for each test."""
    return SharpenProcessor()


@pytest.mark.parametrize(
    "input_filename",
    [
        xfail_unsupported_image_mode()("1"),
        "L",
        xfail_unsupported_image_mode()("LA"),
        "RGB",
        xfail_unsupported_image_mode()("RGBA"),
        "PL",
        xfail_unsupported_image_mode()("PLA"),
        "PRGB",
        xfail_unsupported_image_mode()("PRGBA"),
    ],
)
def test(input_filename: str, processor: SharpenProcessor):
    """Test SharpenProcessor with various image modes.

    Arguments:
        input_filename: Input image filename
        processor: SharpenProcessor fixture instance
    """
    input_path = get_test_input_path(input_filename)
    input_img = Image.open(input_path)
    output_img = processor(input_img)

    assert output_img.mode == get_expected_output_mode(input_img)
    assert output_img.size == input_img.size


@pytest.mark.parametrize("mode", ["L", "RGB"])
def test_sharpen_increases_edge_contrast(mode: str):
    """Increase contrast on both sides of an edge without changing flat interiors.

    Arguments:
        mode: supported image mode
    """
    input_image = Image.new("L", (7, 5), 80)
    input_image.paste(160, (3, 0, 7, 5))
    input_image = input_image.convert(mode)

    output_image = SharpenProcessor()(input_image)
    output_values = output_image.convert("L")

    assert output_values.getpixel((2, 2)) < 80
    assert output_values.getpixel((3, 2)) > 160
    assert output_values.getpixel((1, 2)) == 80
    assert output_values.getpixel((5, 2)) == 160
    assert input_image.convert("L").getpixel((2, 2)) == 80
    assert input_image.convert("L").getpixel((3, 2)) == 160
