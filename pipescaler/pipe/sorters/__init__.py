#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Sorter pipes."""
from __future__ import annotations

from pipescaler.pipe.sorters.alpha_sorter import AlphaSorter
from pipescaler.pipe.sorters.grayscale_sorter import GrayscaleSorter
from pipescaler.pipe.sorters.list_sorter import ListSorter
from pipescaler.pipe.sorters.mode_sorter import ModeSorter
from pipescaler.pipe.sorters.monochrome_sorter import MonochromeSorter
from pipescaler.pipe.sorters.regex_sorter import RegexSorter
from pipescaler.pipe.sorters.size_sorter import SizeSorter
from pipescaler.pipe.sorters.solid_color_sorter import SolidColorSorter

__all__: list[str] = [
    "AlphaSorter",
    "GrayscaleSorter",
    "ListSorter",
    "ModeSorter",
    "MonochromeSorter",
    "RegexSorter",
    "SizeSorter",
    "SolidColorSorter",
]
