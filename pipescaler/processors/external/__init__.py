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

from pipescaler.processors.external.apple_script_processor import AppleScriptProcessor
from pipescaler.processors.external.automator_processor import AutomatorProcessor
from pipescaler.processors.external.pngquant_processor import PngquantProcessor
from pipescaler.processors.external.potrace_processor import PotraceProcessor
from pipescaler.processors.external.texconv_processor import TexconvProcessor
from pipescaler.processors.external.waifu_external_processor import (
    WaifuExternalProcessor,
)

__all__: List[str] = [
    "AppleScriptProcessor",
    "AutomatorProcessor",
    "PngquantProcessor",
    "PotraceProcessor",
    "TexconvProcessor",
    "WaifuExternalProcessor",
]
