#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Validation functions related to images."""

from __future__ import annotations

from collections.abc import Collection

from PIL import Image

from .exceptions import UnsupportedImageModeError
from .functions import remove_palette

__all__ = [
    "validate_image",
    "validate_image_and_convert_mode",
]


def validate_image(
    image: Image.Image, valid_modes: str | Collection[str] | None = None
) -> Image.Image:
    """Remove image palette, if necessary, and validate that mode is among valid modes.

    Arguments:
        image: image to validate
        valid_modes: allowed modes after palette removal; empty or None accepts any mode
    Returns:
        image after palette removal and mode validation
    Raises:
        UnsupportedImageModeError: if an image mode is unsupported
    """
    if image.mode == "P":
        image = remove_palette(image)
    if valid_modes:
        if isinstance(valid_modes, str):
            valid_modes = [valid_modes]
        valid_modes = sorted(valid_modes)
        if image.mode not in valid_modes:
            raise UnsupportedImageModeError(
                f"Mode '{image.mode}' is not among supported modes: {valid_modes}"
            )
    return image


def validate_image_and_convert_mode(
    img: Image.Image,
    valid_modes: str | Collection[str] | None = None,
    convert_mode: str | None = None,
) -> tuple[Image.Image, str]:
    """Validate image mode and convert to specified mode.

    Arguments:
        img: image to validate
        valid_modes: allowed modes after palette removal; empty or None accepts any mode
        convert_mode: optional mode to convert to after validation
    Returns:
        validated image and its mode after palette removal, before conversion
    Raises:
        UnsupportedImageModeError: if the mode after palette removal is unsupported
    """
    img = validate_image(img, valid_modes)
    if convert_mode and img.mode != convert_mode:
        return img.convert(convert_mode), img.mode
    return img, img.mode
