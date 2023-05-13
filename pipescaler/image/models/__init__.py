#!/usr/bin/env python
#  Copyright 2020-2023 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PipeScaler image models package."""
from __future__ import annotations

from pipescaler.image.models.waifu_upconv7 import WaifuUpConv7
from pipescaler.image.models.waifu_vgg7 import WaifuVgg7

__all__ = [
    "WaifuVgg7",
    "WaifuUpConv7",
]
