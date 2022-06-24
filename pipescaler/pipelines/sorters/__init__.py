#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Sorter pipes."""
from __future__ import annotations

from pipescaler.pipelines.sorters.alpha_sorter import AlphaSorter
from pipescaler.pipelines.sorters.grayscale_sorter import GrayscaleSorter
from pipescaler.pipelines.sorters.list_sorter import ListSorter
from pipescaler.pipelines.sorters.mode_sorter import ModeSorter
from pipescaler.pipelines.sorters.monochrome_sorter import MonochromeSorter
from pipescaler.pipelines.sorters.regex_sorter import RegexSorter
from pipescaler.pipelines.sorters.size_sorter import SizeSorter
from pipescaler.pipelines.sorters.solid_color_sorter import SolidColorSorter

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
