#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Sorter stages"""
from __future__ import annotations

from typing import List

from pipescaler.sorters.alpha_sorter import AlphaSorter
from pipescaler.sorters.grayscale_sorter import GrayscaleSorter
from pipescaler.sorters.list_sorter import ListSorter
from pipescaler.sorters.mode_sorter import ModeSorter
from pipescaler.sorters.monochrome_sorter import MonochromeSorter
from pipescaler.sorters.regex_sorter import RegexSorter
from pipescaler.sorters.size_sorter import SizeSorter
from pipescaler.sorters.solid_color_sorter import SolidColorSorter

__all__: List[str] = [
    "AlphaSorter",
    "GrayscaleSorter",
    "ListSorter",
    "ModeSorter",
    "MonochromeSorter",
    "RegexSorter",
    "SizeSorter",
    "SolidColorSorter",
]
