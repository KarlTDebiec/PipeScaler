#!/usr/bin/env python
#   pipescaler/processors/__init__.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from typing import List

from pipescaler.processors.automator_processor import AutomatorProcessor
from pipescaler.processors.copy_processor import CopyFileProcessor
from pipescaler.processors.esrgan_processor import ESRGANProcessor
from pipescaler.processors.flatten_processor import FlattenProcessor
from pipescaler.processors.pixelmator2x_processor import Pixelmator2xProcessor
from pipescaler.processors.pngquant_processor import PngquantProcessor
from pipescaler.processors.potrace_processor import PotraceProcessor
from pipescaler.processors.resize_processor import ResizeProcessor
from pipescaler.processors.side_channel_processor import SideChannelProcessor
from pipescaler.processors.threshold_processor import ThresholdProcessor
from pipescaler.processors.waifu_processor import WaifuProcessor
from pipescaler.processors.waifupixelmator2x_processor import WaifuPixelmator2xProcessor
from pipescaler.processors.xbrz_processor import XbrzProcessor

######################################### ALL ##########################################
__all__: List[str] = [
    "AutomatorProcessor",
    "CopyFileProcessor",
    "ESRGANProcessor",
    "FlattenProcessor",
    "Pixelmator2xProcessor",
    "PotraceProcessor",
    "PngquantProcessor",
    "ResizeProcessor",
    "SideChannelProcessor",
    "ThresholdProcessor",
    "WaifuProcessor",
    "XbrzProcessor",
    "WaifuPixelmator2xProcessor",
]
