#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Image mergers."""
from __future__ import annotations

from pipescaler.image.operators.mergers.alpha_merger import AlphaMerger
from pipescaler.image.operators.mergers.histogram_match_merger import (
    HistogramMatchMerger,
)
from pipescaler.image.operators.mergers.normal_merger import NormalMerger
from pipescaler.image.operators.mergers.palette_match_merger import PaletteMatchMerger

__all__ = [
    "AlphaMerger",
    "HistogramMatchMerger",
    "NormalMerger",
    "PaletteMatchMerger",
]
