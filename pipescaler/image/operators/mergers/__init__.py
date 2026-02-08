#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PipeScaler image merger operators package.

This module may import from: common, core, image.core, image.core.operators

Hierarchy within module:
* alpha_merger / normal_merger / histogram_match_merger / palette_match_merger
"""

from __future__ import annotations

from .alpha_merger import AlphaMerger
from .histogram_match_merger import (
    HistogramMatchMerger,
)
from .normal_merger import NormalMerger
from .palette_match_merger import PaletteMatchMerger

__all__ = [
    "AlphaMerger",
    "HistogramMatchMerger",
    "NormalMerger",
    "PaletteMatchMerger",
]
