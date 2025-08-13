#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PipeScaler image processor operators package."""

from __future__ import annotations

from pipescaler.image.operators.processors.crop_processor import CropProcessor
from pipescaler.image.operators.processors.esrgan_processor import EsrganProcessor
from pipescaler.image.operators.processors.expand_processor import ExpandProcessor
from pipescaler.image.operators.processors.height_to_normal_processor import (
    HeightToNormalProcessor,
)
from pipescaler.image.operators.processors.mode_processor import ModeProcessor
from pipescaler.image.operators.processors.potrace_processor import PotraceProcessor
from pipescaler.image.operators.processors.resize_processor import ResizeProcessor
from pipescaler.image.operators.processors.sharpen_processor import SharpenProcessor
from pipescaler.image.operators.processors.solid_color_processor import (
    SolidColorProcessor,
)
from pipescaler.image.operators.processors.spandrel_processor import SpandrelProcessor
from pipescaler.image.operators.processors.threshold_processor import ThresholdProcessor
from pipescaler.image.operators.processors.waifu_processor import WaifuProcessor
from pipescaler.image.operators.processors.xbrz_processor import XbrzProcessor

__all__ = [
    "CropProcessor",
    "EsrganProcessor",
    "ExpandProcessor",
    "HeightToNormalProcessor",
    "ModeProcessor",
    "PotraceProcessor",
    "ResizeProcessor",
    "SharpenProcessor",
    "SolidColorProcessor",
    "SpandrelProcessor",
    "ThresholdProcessor",
    "WaifuProcessor",
    "XbrzProcessor",
]
