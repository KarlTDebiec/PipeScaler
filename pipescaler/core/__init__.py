#!/usr/bin/env python
#   pipescaler/core/__init__.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Core pipescaler functions, classes, and exceptions"""
from __future__ import annotations

from typing import List

from pipescaler.core.exceptions import TerminusReached, UnsupportedImageModeError
from pipescaler.core.files import get_files
from pipescaler.core.image import (
    crop_image,
    expand_image,
    gaussian_smooth_image,
    normal_map_from_heightmap,
    remove_palette_from_image,
)
from pipescaler.core.merger import Merger
from pipescaler.core.pipe_image import PipeImage
from pipescaler.core.pipeline import Pipeline
from pipescaler.core.processor import Processor
from pipescaler.core.sorter import Sorter
from pipescaler.core.source import Source
from pipescaler.core.splitter import Splitter
from pipescaler.core.stage import Stage, initialize_stage
from pipescaler.core.terminus import Terminus
from pipescaler.core.validation import validate_image, validate_image_and_convert_mode

__all__: List[str] = [
    "Merger",
    "PipeImage",
    "Pipeline",
    "Processor",
    "Sorter",
    "Source",
    "Splitter",
    "Stage",
    "Terminus",
    "TerminusReached",
    "UnsupportedImageModeError",
    "crop_image",
    "expand_image",
    "gaussian_smooth_image",
    "initialize_stage",
    "normal_map_from_heightmap",
    "get_files",
    "remove_palette_from_image",
    "validate_image",
    "validate_image_and_convert_mode",
]
