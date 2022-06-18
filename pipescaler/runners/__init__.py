#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""External tool runners"""
from __future__ import annotations

from pipescaler.runners.apple_script_runner import AppleScriptRunner
from pipescaler.runners.automator_runner import AutomatorRunner
from pipescaler.runners.pngquant_runner import PngquantRunner
from pipescaler.runners.potrace_runner import PotraceRunner
from pipescaler.runners.texconv_runner import TexconvRunner
from pipescaler.runners.waifu_runner import WaifuRunner

__all__: list[str] = [
    "AppleScriptRunner",
    "AutomatorRunner",
    "PngquantRunner",
    "PotraceRunner",
    "TexconvRunner",
    "WaifuRunner",
]
