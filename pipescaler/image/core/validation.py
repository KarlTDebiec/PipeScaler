#!/usr/bin/env python
#  Copyright 2020-2023 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Validation functions related to images."""
from __future__ import annotations

from typing import Collection, Optional

from PIL import Image

from pipescaler.image.core.exceptions import UnsupportedImageModeError
from pipescaler.image.core.functions import remove_palette


def validate_image(
    image: Image.Image, valid_modes: Optional[str | Collection[str]] = None
) -> Image.Image:
    """Remove image palette, if necessary, and validate that mode is among valid modes.

    Arguments:
        image: Image to validate
        valid_modes: Valid modes
    Returns:
        Validated image
    """
    if image.mode == "P":
        image = remove_palette(image)
    if valid_modes:
        if isinstance(valid_modes, str):
            valid_modes = [valid_modes]
        valid_modes = sorted(valid_modes)
        if image.mode not in valid_modes:
            raise UnsupportedImageModeError(
                f"Mode '{image.mode}' is among supported modes: {valid_modes}"
            )
    return image


def validate_image_and_convert_mode(
    image: Image.Image,
    valid_modes: Optional[str | Collection[str]] = None,
    convert_mode: Optional[str] = None,
) -> tuple[Image.Image, str]:
    """Validate image mode and convert to specified mode.

    Arguments:
        image: Image to validate
        valid_modes: Valid modes
        convert_mode: Mode to convert to
    Returns:
        Validated image and original mode
    """
    image = validate_image(image, valid_modes)
    if convert_mode and image.mode != convert_mode:
        return (image.convert(convert_mode), image.mode)
    return (image, image.mode)
