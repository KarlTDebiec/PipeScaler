#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PipeScaler image pipeline sorters package.

This module may import from: common, core.pipelines, image.core.pipelines

Hierarchy within module:
* alpha_sorter / grayscale_sorter / mode_sorter / monochrome_sorter / size_sorter / solid_color_sorter
"""

from __future__ import annotations

from .alpha_sorter import AlphaSorter
from .grayscale_sorter import GrayscaleSorter
from .mode_sorter import ModeSorter
from .monochrome_sorter import MonochromeSorter
from .size_sorter import SizeSorter
from .solid_color_sorter import SolidColorSorter

__all__ = [
    "AlphaSorter",
    "GrayscaleSorter",
    "ModeSorter",
    "MonochromeSorter",
    "SizeSorter",
    "SolidColorSorter",
]
