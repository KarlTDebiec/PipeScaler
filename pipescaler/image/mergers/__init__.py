#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Merger image operators."""
from __future__ import annotations

from pipescaler.image.mergers.alpha_merger import AlphaMerger
from pipescaler.image.mergers.histogram_match_merger import HistogramMatchMerger
from pipescaler.image.mergers.normal_merger import NormalMerger
from pipescaler.image.mergers.palette_match_merger import PaletteMatchMerger

__all__: list[str] = [
    "AlphaMerger",
    "HistogramMatchMerger",
    "NormalMerger",
    "PaletteMatchMerger",
]