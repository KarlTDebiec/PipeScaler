#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Image-related functions for testing."""
from PIL import Image

from pipescaler.core import remove_palette_from_image


def get_expected_output_mode(input_image: Image.Image) -> str:
    """Get expected output mode of image after processing.

    Args:
        input_image: Input image
    Returns:
        Expected output mode of image after processing
    """
    if input_image.mode == "P":
        return remove_palette_from_image(input_image).mode
    else:
        return input_image.mode
