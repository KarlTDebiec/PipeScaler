#!/usr/bin/env python
#  Copyright (C) 2020-2022. Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Abstract base classes and functions for image manipulation."""
from __future__ import annotations

from pipescaler.core.image.functions import (
    convert_mode,
    crop_image,
    expand_image,
    generate_normal_map_from_height_map_image,
    get_font_size,
    get_palette,
    get_perceptually_weighted_distance,
    get_text_size,
    hstack_images,
    is_monochrome,
    label_image,
    remove_palette,
    smooth_image,
    vstack_images,
)
from pipescaler.core.image.operator import Operator
from pipescaler.core.image.operators.merger import Merger
from pipescaler.core.image.operators.processor import Processor
from pipescaler.core.image.operators.splitter import Splitter

__all__: list[str] = [
    "Merger",
    "Operator",
    "Processor",
    "Splitter",
    "convert_mode",
    "crop_image",
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
    "vstack_images",
]
