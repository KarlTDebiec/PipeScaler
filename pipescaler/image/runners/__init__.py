#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PipeScaler image external image tool runners package."""
from __future__ import annotations

from pipescaler.image.runners.pngquant_runner import PngquantRunner
from pipescaler.image.runners.potrace_runner import PotraceRunner
from pipescaler.image.runners.texconv_runner import TexconvRunner
from pipescaler.image.runners.waifu_runner import WaifuRunner

__all__ = [
    "PngquantRunner",
    "PotraceRunner",
    "TexconvRunner",
    "WaifuRunner",
]
