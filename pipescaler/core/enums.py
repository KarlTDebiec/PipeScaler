#!/usr/bin/env python
#   pipescaler/core/enums.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Enums."""
from __future__ import annotations

from enum import Enum, auto


class AlphaMode(Enum):
    """Mode of output alpha image"""

    L = auto()
    L_OR_1 = auto()
    L_OR_1_FILL = auto()


class FillMode(Enum):
    BASIC = auto()
    MATCH_PALETTE = auto()


class PaletteMatchMode(Enum):
    """Mode of matching to perform"""

    BASIC = auto()
    LOCAL = auto()
