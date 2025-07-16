#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Image-related functions for testing."""

from __future__ import annotations

from functools import partial

from PIL import Image
from pytest import mark, param

from pipescaler.image.core.exceptions import UnsupportedImageModeError
from pipescaler.image.core.functions import remove_palette


def get_expected_output_mode(input_image: Image.Image) -> str:
    """Get expected output mode of image after processing.

    Arguments:
        input_image: Input image
    Returns:
        Expected output mode of image after processing
    """
    if input_image.mode == "P":
        return remove_palette(input_image).mode
    return input_image.mode


def xfail_unsupported_image_mode(inner: partial | None = None) -> partial:
    """Mark test to be expected to fail due to an unsupported image mode.

    Arguments:
        inner: Nascent partial function of pytest.param with additional marks
    Returns:
        Partial function of pytest.param with marks
    """
    marks = [mark.xfail(raises=UnsupportedImageModeError)]
    if inner:
        marks.extend(inner.keywords["marks"])
    return partial(param, marks=marks)
