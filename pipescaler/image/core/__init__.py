#  Copyright 2020-2023 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""PipeScaler image core package."""
from __future__ import annotations

from pipescaler.image.core.enums import AlphaMode, MaskFillMode, PaletteMatchMode
from pipescaler.image.core.exceptions import UnsupportedImageModeError
from pipescaler.image.core.functions import (
    convert_mode,
    crop_image,
    expand_image,
    generate_normal_map_from_height_map_image,
    get_font_size,
    get_palette,
    get_text_size,
    hstack_images,
    is_monochrome,
    label_image,
    remove_palette,
    smooth_image,
    vstack_images,
)
from pipescaler.image.core.image_operator import ImageOperator
from pipescaler.image.core.numba import get_perceptually_weighted_distance
from pipescaler.image.core.sorting import citra_sort, dolphin_sort, texmod_sort
from pipescaler.image.core.validation import (
    validate_image,
    validate_image_and_convert_mode,
)

__all__ = [
    "AlphaMode",
    "ImageOperator",
    "MaskFillMode",
    "PaletteMatchMode",
    "UnsupportedImageModeError",
    "citra_sort",
    "convert_mode",
    "crop_image",
    "dolphin_sort",
    "expand_image",
    "generate_normal_map_from_height_map_image",
    "get_palette",
    "get_font_size",
    "get_text_size",
    "get_perceptually_weighted_distance",
    "hstack_images",
    "is_monochrome",
    "label_image",
    "remove_palette",
    "smooth_image",
    "texmod_sort",
    "validate_image",
    "validate_image_and_convert_mode",
    "vstack_images",
]
