#!/usr/bin/env python
#   pipescaler/core/validation.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Core pipescaler functions for validation"""
from __future__ import annotations

from typing import List, Tuple, Union

from PIL import Image

from pipescaler.common import validate_input_path
from pipescaler.core.exception import UnsupportedImageModeError
from pipescaler.core.image import remove_palette_from_image


def validate_image(infile: str, valid_modes: Union[str, List[str]]) -> Image.Image:
    """
    Validate that image exists and is of a valid mode, and remove palette if present

    Arguments:
        infile: Image infile
        valid_modes: Valid image modes

    Returns:
        Image
    """
    if isinstance(valid_modes, str):
        valid_modes = [valid_modes]

    # If infile is a temporary file, and an UnsupportedImageModeError is raised, a
    # PermissionError is raised when attempting to remove the temporary file. This
    # appears to be due to a bug (or just unexpected behavior) in pillow that keeps the
    # file open. Appending '.copy()' mysteriously works around this and closes the file
    image = Image.open(validate_input_path(infile)).copy()
    if image.mode == "P":
        image = remove_palette_from_image(image)
    if image.mode not in valid_modes:
        raise UnsupportedImageModeError(
            f"Mode '{image.mode}' of image '{infile}' is not supported"
        )

    return image


def validate_image_and_convert_mode(
    infile: str,
    valid_modes: Union[str, List[str]],
    convert_mode: str,
) -> Tuple[Image.Image, str]:
    """
    Validate that image exists and is of a valid mode, remove palette if present, and
    convert it to provided mode

    Arguments:
        infile: Image infile
        valid_modes: Valid image modes
        convert_mode: Mode to which to convert image

    Returns:
        Tuple of image and image's original mode
    """
    image = validate_image(infile, valid_modes)

    if image.mode != convert_mode:
        return (image.convert(convert_mode), image.mode)
    return (image, image.mode)
