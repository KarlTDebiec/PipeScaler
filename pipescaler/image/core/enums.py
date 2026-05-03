#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Image enumerations."""

from __future__ import annotations

from enum import Enum, auto

__all__ = [
    "AlphaMode",
    "MaskFillMode",
    "PaletteMatchMode",
]


class AlphaMode(Enum):
    """Mode of alpha channel handling to perform."""

    GRAYSCALE = auto()
    """Convert alpha channel to grayscale."""
    MONOCHROME_OR_GRAYSCALE = auto()
    """Convert alpha channel to monochrome when possible, otherwise grayscale."""


class MaskFillMode(Enum):
    """Mode of mask filling to perform."""

    BASIC = auto()
    """Fill mask using the basic fill strategy."""
    MATCH_PALETTE = auto()
    """Fill mask using palette matching."""


class PaletteMatchMode(Enum):
    """Mode of matching to perform."""

    BASIC = auto()
    """Match against the global palette."""
    LOCAL = auto()
    """Match against local palettes."""
