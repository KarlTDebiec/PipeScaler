#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""External executable processor stages."""
from __future__ import annotations

from pipescaler.image.processors.external.automator_processor import AutomatorProcessor
from pipescaler.runners.pngquant_runner import PngquantRunner
from pipescaler.runners.texconv_runner import TexconvRunner

__all__: list[str] = [
    "AppleScriptProcessor",
    "AutomatorProcessor",
    "PngquantRunner",
    "PotraceProcessor",
    "TexconvRunner",
    "WaifuExternalProcessor",
]
