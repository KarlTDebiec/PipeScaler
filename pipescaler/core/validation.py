#!/usr/bin/env python
#   pipescaler/core/validation.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
from __future__ import annotations

from typing import List, Optional, Tuple, Union

from PIL import Image

from pipescaler.core.exception import UnsupportedImageModeError
from pipescaler.core.image import remove_palette_from_image


def validate_image(infile: str, supported_modes: Union[str, List[str]]) -> Image.Image:
    if isinstance(supported_modes, str):
        supported_modes = [supported_modes]

    image = Image.open(infile)
    if image.mode == "P":
        image = remove_palette_from_image(image)
    if image.mode not in supported_modes:
        raise UnsupportedImageModeError(
            f"Mode '{image.mode}' of image '{infile}' is not supported"
        )

    return image


def validate_image_and_convert_mode(
    infile: str,
    supported_modes: Union[str, List[str]],
    convert_mode: Optional[str] = None,
) -> Tuple[Image.Image, str]:
    image = validate_image(infile, supported_modes)

    if convert_mode is not None and image.mode != convert_mode:
        return (image.convert(convert_mode), image.mode)
    else:
        return (image, image.mode)
