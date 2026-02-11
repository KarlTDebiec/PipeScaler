#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Validation functions related to images."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .exceptions import UnsupportedImageModeError
from .functions import remove_palette

if TYPE_CHECKING:
    from collections.abc import Collection

    from PIL import Image


def validate_image(
    image: Image.Image, valid_modes: str | Collection[str] | None = None
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
    img: Image.Image,
    valid_modes: str | Collection[str] | None = None,
    convert_mode: str | None = None,
) -> tuple[Image.Image, str]:
    """Validate image mode and convert to specified mode.

    Arguments:
        img: Image to validate
        valid_modes: Valid modes
        convert_mode: Mode to convert to
    Returns:
        Validated image and original mode
    """
    img = validate_image(img, valid_modes)
    if convert_mode and img.mode != convert_mode:
        return img.convert(convert_mode), img.mode
    return img, img.mode
