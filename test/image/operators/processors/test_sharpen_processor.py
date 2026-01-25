#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for SharpenProcessor."""

import pytest
from PIL import Image

from pipescaler.image.operators.processors import SharpenProcessor
from pipescaler.image.testing import (
    get_expected_output_mode,
    xfail_unsupported_image_mode,
)
from pipescaler.testing.file import get_test_input_path
from pipescaler.testing.fixture import parametrized_fixture


@parametrized_fixture(
    cls=SharpenProcessor,
    params=[
        {},
    ],
)
def processor(request) -> SharpenProcessor:
    """Pytest fixture that provides a SharpenProcessor instance.

    Arguments:
        request: Pytest request fixture containing parameters
    Returns:
        Configured SharpenProcessor instance
    """
    return SharpenProcessor(**request.param)


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
