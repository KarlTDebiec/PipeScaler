#!/usr/bin/env python
#   pipescaler/core/__init__.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
""""""
from __future__ import annotations

from typing import List

from pipescaler.core.stage import Stage
from pipescaler.core.merger import Merger
from pipescaler.core.processor import Processor
from pipescaler.core.sorter import Sorter
from pipescaler.core.source import Source
from pipescaler.core.splitter import Splitter
from pipescaler.core.terminus import Terminus

from pipescaler.core.exceptions import (
    TerminusReached,
    UnsupportedImageModeError,
    UnsupportedPlatformError,
)
from pipescaler.core.misc import (
    crop_image,
    expand_image,
    gaussian_smooth_image,
    normal_map_from_heightmap,
    parse_file_list,
    remove_palette_from_image,
)
from pipescaler.core.pipe_image import PipeImage
from pipescaler.core.pipeline import Pipeline

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
    "UnsupportedPlatformError",
    "crop_image",
    "expand_image",
    "gaussian_smooth_image",
    "normal_map_from_heightmap",
    "parse_file_list",
    "remove_palette_from_image",
]
