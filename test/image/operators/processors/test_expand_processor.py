#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for ExpandProcessor."""

from __future__ import annotations

import pytest
from PIL import Image

from pipescaler.image.operators.processors import ExpandProcessor
from pipescaler.image.testing import get_expected_output_mode
from pipescaler.testing.file import get_test_input_path


@pytest.fixture
def processor() -> ExpandProcessor:
    """Provide a fresh ExpandProcessor instance for each test."""
    return ExpandProcessor(pixels=(4, 4, 4, 4))


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
    """Test ExpandProcessor with various image modes.

    Arguments:
        input_filename: Input image filename
        processor: ExpandProcessor fixture instance
    """
    input_path = get_test_input_path(input_filename)
    input_img = Image.open(input_path)
    output_img = processor(input_img)

    assert output_img.mode == get_expected_output_mode(input_img)
    assert output_img.size == (
        input_img.size[0] + processor.left + processor.right,
        input_img.size[1] + processor.top + processor.bottom,
    )
