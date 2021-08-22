#!/usr/bin/env python
#   pipescaler/mergers/__init__.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
""""""
from __future__ import annotations

from typing import List

from pipescaler.mergers.alpha_merger import AlphaMerger
from pipescaler.mergers.color_match_merger import ColorMatchMerger
from pipescaler.mergers.color_to_alpha_merger import ColorToAlphaMerger
from pipescaler.mergers.normal_merger import NormalMerger

__all__: List[str] = [
    "AlphaMerger",
    "ColorMatchMerger",
    "ColorToAlphaMerger",
    "NormalMerger",
]
