#!/usr/bin/env python
#   pipescaler/mergers/__init__.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Merger stages"""
from __future__ import annotations

from typing import List

from pipescaler.mergers.alpha_merger import AlphaMerger
from pipescaler.mergers.histogram_match_merger import HistogramMatchMerger
from pipescaler.mergers.normal_merger import NormalMerger
from pipescaler.mergers.palette_match_merger import PaletteMatchMerger

__all__: List[str] = [
    "AlphaMerger",
    "HistogramMatchMerger",
    "NormalMerger",
    "PaletteMatchMerger",
]
