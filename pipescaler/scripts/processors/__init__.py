#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
from __future__ import annotations

from pipescaler.scripts.processors.crop_command_line_tool import CropCommandLineTool
from pipescaler.scripts.processors.esrgan_command_line_tool import ESRGANCommandLineTool
from pipescaler.scripts.processors.expand_command_line_tool import ExpandCommandLineTool
from pipescaler.scripts.processors.height_to_normal_command_line_tool import (
    HeightToNormalCommandLineTool,
)
from pipescaler.scripts.processors.mode_command_line_tool import ModeCommandLineTool
from pipescaler.scripts.processors.resize_command_line_tool import ResizeCommandLineTool
from pipescaler.scripts.processors.sharpen_command_line_tool import (
    SharpenCommandLineTool,
)
from pipescaler.scripts.processors.solid_color_command_line_tool import (
    SolidColorCommandLineTool,
)
from pipescaler.scripts.processors.threshold_command_line_tool import (
    ThresholdCommandLineTool,
)
from pipescaler.scripts.processors.waifu_command_line_tool import WaifuCommandLineTool
from pipescaler.scripts.processors.web_command_line_tool import WebCommandLineTool
from pipescaler.scripts.processors.xbrz_command_line_tool import XbrzCommandLineTool

__all__: list[str] = [
    "CropCommandLineTool",
    "ESRGANCommandLineTool",
    "ExpandCommandLineTool",
    "HeightToNormalCommandLineTool",
    "ModeCommandLineTool",
    "ResizeCommandLineTool",
    "SharpenCommandLineTool",
    "SolidColorCommandLineTool",
    "ThresholdCommandLineTool",
    "WaifuCommandLineTool",
    "WebCommandLineTool",
    "XbrzCommandLineTool",
]
