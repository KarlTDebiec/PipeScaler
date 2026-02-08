#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PipeScaler image processor operators package.

This module may import from: common, core, image.core, image.core.operators

Hierarchy within module:
* crop_processor / expand_processor / mode_processor / resize_processor / solid_color_processor / threshold_processor
* height_to_normal_processor / sharpen_processor / potrace_processor / xbrz_processor / spandrel_processor
"""

from __future__ import annotations

from .crop_processor import CropProcessor
from .expand_processor import ExpandProcessor
from .height_to_normal_processor import (
    HeightToNormalProcessor,
)
from .mode_processor import ModeProcessor
from .potrace_processor import PotraceProcessor
from .resize_processor import ResizeProcessor
from .sharpen_processor import SharpenProcessor
from .solid_color_processor import (
    SolidColorProcessor,
)
from .spandrel_processor import SpandrelProcessor
from .threshold_processor import ThresholdProcessor
from .xbrz_processor import XbrzProcessor

__all__ = [
    "CropProcessor",
    "ExpandProcessor",
    "HeightToNormalProcessor",
    "ModeProcessor",
    "PotraceProcessor",
    "ResizeProcessor",
    "SharpenProcessor",
    "SolidColorProcessor",
    "SpandrelProcessor",
    "ThresholdProcessor",
    "XbrzProcessor",
]
