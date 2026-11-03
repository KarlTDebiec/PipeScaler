#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Image-related functions for testing."""

from __future__ import annotations

from PIL import Image

from .core.functions import remove_palette

__all__ = ["get_expected_output_mode"]


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
