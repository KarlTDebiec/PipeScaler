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

from pipescaler.models.waifu_upcon7 import WaifuUpconv7

__all__: List[str] = [
    "WaifuUpconv7",
]
