#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Image Sorters."""
from __future__ import annotations

from pipescaler.pipelines.sorters.image.alpha_sorter import AlphaSorter
from pipescaler.pipelines.sorters.image.grayscale_sorter import GrayscaleSorter
from pipescaler.pipelines.sorters.image.mode_sorter import ModeSorter
from pipescaler.pipelines.sorters.image.monochrome_sorter import MonochromeSorter
from pipescaler.pipelines.sorters.image.size_sorter import SizeSorter
from pipescaler.pipelines.sorters.image.solid_color_sorter import SolidColorSorter

__all__ = [
    "AlphaSorter",
    "GrayscaleSorter",
    "ModeSorter",
    "MonochromeSorter",
    "SizeSorter",
    "SolidColorSorter",
]
