#!/usr/bin/env python
#   pipescaler/models/__init__.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Models"""
from __future__ import annotations

from typing import List

from pipescaler.models.waifu_upconv7 import WaifuUpConv7
from pipescaler.models.waifu_vgg7 import WaifuVgg7

__all__: List[str] = [
    "WaifuVgg7",
    "WaifuUpConv7",
]