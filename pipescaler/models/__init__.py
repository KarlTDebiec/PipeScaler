#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""PyTorch models."""
from __future__ import annotations

from pipescaler.models.waifu_upconv7 import WaifuUpConv7
from pipescaler.models.waifu_vgg7 import WaifuVgg7

__all__: list[str] = [
    "WaifuVgg7",
    "WaifuUpConv7",
]
