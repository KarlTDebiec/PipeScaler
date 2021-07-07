#!/usr/bin/env python
#   pipescaler/processors/__init__.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from typing import List

from pipescaler.processors.automator_processor import AutomatorProcessor
from pipescaler.processors.esrgan_processor import ESRGANProcessor
from pipescaler.processors.pngquant_processor import PngquantProcessor
from pipescaler.processors.potrace_processor import PotraceProcessor
from pipescaler.processors.resize_processor import ResizeProcessor
from pipescaler.processors.side_channel_processor import SideChannelProcessor
from pipescaler.processors.texconv_processor import TexconvProcessor
from pipescaler.processors.threshold_processor import ThresholdProcessor
from pipescaler.processors.waifu_processor import WaifuProcessor
from pipescaler.processors.xbrz_processor import XbrzProcessor
from pipescaler.processors.mode_processor import ModeProcessor

######################################### ALL ##########################################
__all__: List[str] = [
    "AutomatorProcessor",
    "ESRGANProcessor",
    "ModeProcessor",
    "PotraceProcessor",
    "PngquantProcessor",
    "ResizeProcessor",
    "SideChannelProcessor",
    "TexconvProcessor",
    "ThresholdProcessor",
    "WaifuProcessor",
    "XbrzProcessor",
]
