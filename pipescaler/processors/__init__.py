#!/usr/bin/env python
#   pipescaler/processors/__init__.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from __future__ import annotations

from typing import List

from pipescaler.processors.AutomatorProcessor import AutomatorProcessor
from pipescaler.processors.CopyFileProcessor import CopyFileProcessor
from pipescaler.processors.ESRGANProcessor import ESRGANProcessor
from pipescaler.processors.FlattenProcessor import FlattenProcessor
from pipescaler.processors.Pixelmator2xProcessor import Pixelmator2xProcessor
from pipescaler.processors.PngquantProcessor import PngquantProcessor
from pipescaler.processors.PotraceProcessor import PotraceProcessor
from pipescaler.processors.ResizeProcessor import ResizeProcessor
from pipescaler.processors.SideChannelProcessor import SideChannelProcessor
from pipescaler.processors.ThresholdProcessor import ThresholdProcessor
from pipescaler.processors.WaifuPixelmator2xTransparentProcessor import (
    WaifuPixelmator2xTransparentProcessor)
from pipescaler.processors.WaifuProcessor import WaifuProcessor
from pipescaler.processors.XbrzProcessor import XbrzProcessor

##################################### ALL #####################################
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
    "WaifuPixelmator2xTransparentProcessor"
]
