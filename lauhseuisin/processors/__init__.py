#!python
#   lauhseuisin/processors/__init__.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from __future__ import annotations

from typing import List

from lauhseuisin.processors.AutomatorProcessor import AutomatorProcessor
from lauhseuisin.processors.CopyFileProcessor import CopyFileProcessor
from lauhseuisin.processors.ESRGANProcessor import ESRGANProcessor
from lauhseuisin.processors.FlattenProcessor import FlattenProcessor
from lauhseuisin.processors.ImageMagickProcessor import ImageMagickProcessor
from lauhseuisin.processors.ResizeProcessor import ResizeProcessor
from lauhseuisin.processors.ThresholdProcessor import ThresholdProcessor
from lauhseuisin.processors.WaifuProcessor import WaifuProcessor
from lauhseuisin.processors.XbrzProcessor import XbrzProcessor

##################################### ALL #####################################
__all__: List[str] = [
    "AutomatorProcessor",
    "CopyFileProcessor",
    "ESRGANProcessor",
    "FlattenProcessor",
    "ImageMagickProcessor",
    "ResizeProcessor",
    "ThresholdProcessor",
    "WaifuProcessor",
    "XbrzProcessor"
]
