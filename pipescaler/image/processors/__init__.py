#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Processor stages."""
from __future__ import annotations

from pipescaler.image.processors.crop_processor import CropProcessor
from pipescaler.image.processors.esrgan_processor import EsrganProcessor
from pipescaler.image.processors.expand_processor import ExpandProcessor
from pipescaler.image.processors.height_to_normal_processor import (
    HeightToNormalProcessor,
)
from pipescaler.image.processors.mode_processor import ModeProcessor
from pipescaler.image.processors.potrace_processor import PotraceProcessor
from pipescaler.image.processors.resize_processor import ResizeProcessor
from pipescaler.image.processors.sharpen_processor import SharpenProcessor
from pipescaler.image.processors.solid_color_processor import SolidColorProcessor
from pipescaler.image.processors.threshold_processor import ThresholdProcessor
from pipescaler.image.processors.waifu_external_processor import WaifuExternalProcessor
from pipescaler.image.processors.waifu_processor import WaifuProcessor
from pipescaler.image.processors.web_processor import WebProcessor
from pipescaler.image.processors.xbrz_processor import XbrzProcessor

__all__: list[str] = [
    "CropProcessor",
    "EsrganProcessor",
    "ExpandProcessor",
    "HeightToNormalProcessor",
    "ModeProcessor",
    "PotraceProcessor",
    "ResizeProcessor",
    "SharpenProcessor",
    "SolidColorProcessor",
    "ThresholdProcessor",
    "WaifuExternalProcessor",
    "WaifuProcessor",
    "WebProcessor",
    "XbrzProcessor",
]
