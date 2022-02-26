#!/usr/bin/env python
#   pipescaler/processors/__init__.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Processor stages"""
from __future__ import annotations

from typing import List

from pipescaler.processors.external import (
    AppleScriptProcessor,
    AutomatorProcessor,
    PngquantProcessor,
    PotraceProcessor,
    TexconvProcessor,
    WaifuExternalProcessor,
)
from pipescaler.processors.gui import GigapixelAiProcessor
from pipescaler.processors.image import (
    CropProcessor,
    ESRGANProcessor,
    ExpandProcessor,
    HeightToNormalProcessor,
    ModeProcessor,
    ResizeProcessor,
    SolidColorProcessor,
    ThresholdProcessor,
    WaifuProcessor,
    XbrzProcessor,
)
from pipescaler.processors.side_channel_processor import SideChannelProcessor
from pipescaler.processors.web_processor import WebProcessor

__all__: List[str] = [
    "AppleScriptProcessor",
    "AutomatorProcessor",
    "CropProcessor",
    "ESRGANProcessor",
    "ExpandProcessor",
    "GigapixelAiProcessor",
    "HeightToNormalProcessor",
    "ModeProcessor",
    "PngquantProcessor",
    "PotraceProcessor",
    "ResizeProcessor",
    "SideChannelProcessor",
    "SolidColorProcessor",
    "TexconvProcessor",
    "ThresholdProcessor",
    "WaifuExternalProcessor",
    "WaifuProcessor",
    "WebProcessor",
    "XbrzProcessor",
]
