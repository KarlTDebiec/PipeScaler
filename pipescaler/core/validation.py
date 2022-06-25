#!/usr/bin/env python
#  Copyright (C) 2020-2022. Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Functions for validation."""
from __future__ import annotations

from typing import Collection, Optional, Union

from PIL import Image

from pipescaler.core.exceptions import UnsupportedImageModeError
from pipescaler.core.image import remove_palette


def validate_image(
    image: Image.Image, valid_modes: Union[str, Collection[str]]
) -> Image.Image:
    """Validate image mode.

    Arguments:
        image: Image to validate
        valid_modes: Valid modes
    Returns:
        Validated image
    """
    if image.mode == "P":
        image = remove_palette(image)
    if image.mode not in valid_modes:
        raise UnsupportedImageModeError(f"Mode '{image.mode}' is not supported")
    return image


def validate_image_and_convert_mode(
    image: Image.Image,
    valid_modes: Union[str, Collection[str]],
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
    if convert_mode is not None and image.mode != convert_mode:
        return (image.convert(convert_mode), image.mode)
    return (image, image.mode)
