#!/usr/bin/env python
#   pipescaler/processors/image/__init__.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Image-based Processor stages"""
from __future__ import annotations

from typing import List

from pipescaler.processors.image.crop_processor import CropProcessor
from pipescaler.processors.image.esrgan_processor import ESRGANProcessor
from pipescaler.processors.image.expand_processor import ExpandProcessor
from pipescaler.processors.image.height_to_normal_processor import (
    HeightToNormalProcessor,
)
from pipescaler.processors.image.mode_processor import ModeProcessor
from pipescaler.processors.image.resize_processor import ResizeProcessor
from pipescaler.processors.image.sharpen_processor import SharpenProcessor
from pipescaler.processors.image.solid_color_processor import SolidColorProcessor
from pipescaler.processors.image.threshold_processor import ThresholdProcessor
from pipescaler.processors.image.waifu_processor import WaifuProcessor
from pipescaler.processors.image.xbrz_processor import XbrzProcessor

__all__: List[str] = [
    "CropProcessor",
    "ESRGANProcessor",
    "ExpandProcessor",
    "HeightToNormalProcessor",
    "ModeProcessor",
    "ResizeProcessor",
    "SharpenProcessor",
    "SolidColorProcessor",
    "ThresholdProcessor",
    "WaifuProcessor",
    "XbrzProcessor",
]
