#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Image enumerations."""

from __future__ import annotations

from enum import Enum, auto


class AlphaMode(Enum):
    """Mode of alpha channel handling to perform."""

    GRAYSCALE = auto()
    MONOCHROME_OR_GRAYSCALE = auto()


class MaskFillMode(Enum):
    """Mode of mask filling to perform."""

    BASIC = auto()
    MATCH_PALETTE = auto()


class PaletteMatchMode(Enum):
    """Mode of matching to perform."""

    BASIC = auto()
    LOCAL = auto()
