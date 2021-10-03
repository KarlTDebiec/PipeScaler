#!/usr/bin/env python
#   pipescaler/processors/__init__.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
from __future__ import annotations

from typing import List

from pipescaler.processors.apple_script_external_processor import (
    AppleScriptExternalProcessor,
)
from pipescaler.processors.automator_external_processor import (
    AutomatorExternalProcessor,
)
from pipescaler.processors.crop_processor import CropProcessor
from pipescaler.processors.esrgan_processor import ESRGANProcessor
from pipescaler.processors.expand_processor import ExpandProcessor
from pipescaler.processors.height_to_normal_processor import HeightToNormalProcessor
from pipescaler.processors.mode_processor import ModeProcessor
from pipescaler.processors.pngquant_external_processor import PngquantExternalProcessor
from pipescaler.processors.potrace_external_processor import PotraceExternalProcessor
from pipescaler.processors.resize_processor import ResizeProcessor
from pipescaler.processors.side_channel_processor import SideChannelProcessor
from pipescaler.processors.solid_color_processor import SolidColorProcessor
from pipescaler.processors.texconv_external_processor import TexconvExternalProcessor
from pipescaler.processors.threshold_processor import ThresholdProcessor
from pipescaler.processors.waifu_external_processor import WaifuExternalProcessor
from pipescaler.processors.web_processor import WebProcessor
from pipescaler.processors.xbrz_processor import XbrzProcessor

__all__: List[str] = [
    "AppleScriptExternalProcessor",
    "AutomatorExternalProcessor",
    "CropProcessor",
    "ESRGANProcessor",
    "ExpandProcessor",
    "HeightToNormalProcessor",
    "ModeProcessor",
    "PngquantExternalProcessor",
    "PotraceExternalProcessor",
    "ResizeProcessor",
    "SideChannelProcessor",
    "SolidColorProcessor",
    "TexconvExternalProcessor",
    "ThresholdProcessor",
    "WaifuExternalProcessor",
    "WebProcessor",
    "XbrzProcessor",
]
