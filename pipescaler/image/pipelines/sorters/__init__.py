#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PipeScaler image pipeline sorters package."""

from __future__ import annotations

from pipescaler.image.pipelines.sorters.alpha_sorter import AlphaSorter
from pipescaler.image.pipelines.sorters.grayscale_sorter import GrayscaleSorter
from pipescaler.image.pipelines.sorters.mode_sorter import ModeSorter
from pipescaler.image.pipelines.sorters.monochrome_sorter import MonochromeSorter
from pipescaler.image.pipelines.sorters.size_sorter import SizeSorter
from pipescaler.image.pipelines.sorters.solid_color_sorter import SolidColorSorter

__all__ = [
    "AlphaSorter",
    "GrayscaleSorter",
    "ModeSorter",
    "MonochromeSorter",
    "SizeSorter",
    "SolidColorSorter",
]
