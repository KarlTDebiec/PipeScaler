#!/usr/bin/env python
#   pipescaler/sorters/__init__.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
""""""
from __future__ import annotations

from typing import List

from pipescaler.sorters.alpha_sorter import AlphaSorter
from pipescaler.sorters.mode_sorter import ModeSorter
from pipescaler.sorters.list_sorter import ListSorter
from pipescaler.sorters.regex_sorter import RegexSorter
from pipescaler.sorters.grayscale_sorter import GrayscaleSorter
from pipescaler.sorters.size_sorter import SizeSorter
from pipescaler.sorters.solid_color_sorter import SolidColorSorter

__all__: List[str] = [
    "AlphaSorter",
    "GrayscaleSorter",
    "ListSorter",
    "ModeSorter",
    "RegexSorter",
    "SizeSorter",
    "SolidColorSorter",
]
