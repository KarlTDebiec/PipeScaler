#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Core pipescaler functions, classes, and exceptions"""
from __future__ import annotations

from pipescaler.core.enum import AlphaMode, MaskFillMode, PaletteMatchMode
from pipescaler.core.exception import TerminusReached, UnsupportedImageModeError
from pipescaler.core.external_processor import ExternalProcessor
from pipescaler.core.file import get_files
from pipescaler.core.image import (
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
    remove_palette_from_image,
    smooth_image,
    vstack_images,
)
from pipescaler.core.image_processor import ImageProcessor
from pipescaler.core.merger import Merger
from pipescaler.core.pipe_image import PipeImage
from pipescaler.core.pipeline import Pipeline
from pipescaler.core.processor import Processor
from pipescaler.core.pytorch_processor import PyTorchProcessor
from pipescaler.core.sorter import Sorter
from pipescaler.core.source import Source
from pipescaler.core.splitter import Splitter
from pipescaler.core.stage import Stage, initialize_stage
from pipescaler.core.terminus import Terminus
from pipescaler.core.validation import validate_image, validate_image_and_convert_mode

__all__: list[str] = [
    "AlphaMode",
    "ExternalProcessor",
    "MaskFillMode",
    "ImageProcessor",
    "Merger",
    "PaletteMatchMode",
    "PipeImage",
    "Pipeline",
    "Processor",
    "PyTorchProcessor",
    "Sorter",
    "Source",
    "Splitter",
    "Stage",
    "Terminus",
    "TerminusReached",
    "UnsupportedImageModeError",
    "convert_mode",
    "crop_image",
    "expand_image",
    "smooth_image",
    "initialize_stage",
    "generate_normal_map_from_height_map_image",
    "get_palette",
    "get_files",
    "get_font_size",
    "get_text_size",
    "is_monochrome",
    "label_image",
    "remove_palette_from_image",
    "hstack_images",
    "validate_image",
    "validate_image_and_convert_mode",
    "vstack_images",
]
