#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
from __future__ import annotations

from pipescaler.cl.processors.crop_cl import CropCL
from pipescaler.cl.processors.esrgan_cl import EsrganCL
from pipescaler.cl.processors.expand_cl import ExpandCL
from pipescaler.cl.processors.height_to_normal_cl import HeightToNormalCL
from pipescaler.cl.processors.mode_cl import ModeCL
from pipescaler.cl.processors.resize_cl import ResizeCL
from pipescaler.cl.processors.sharpen_cl import SharpenCL
from pipescaler.cl.processors.solid_color_cl import SolidColorCL
from pipescaler.cl.processors.threshold_cl import ThresholdCL
from pipescaler.cl.processors.waifu_cl import WaifuCL
from pipescaler.cl.processors.web_cl import WebCL
from pipescaler.cl.processors.xbrz_cl import XbrzCL

__all__: list[str] = [
    "CropCL",
    "EsrganCL",
    "ExpandCL",
    "HeightToNormalCL",
    "ModeCL",
    "ResizeCL",
    "SharpenCL",
    "SolidColorCL",
    "ThresholdCL",
    "WaifuCL",
    "WebCL",
    "XbrzCL",
]
