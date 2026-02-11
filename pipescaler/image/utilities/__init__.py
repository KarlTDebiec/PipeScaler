#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PipeScaler image utilities package.

This module may import from: common, core, image.core

Hierarchy within module:
* palette_matcher / local_palette_matcher / local_palette_shader_matcher / mask_filler
"""

from __future__ import annotations

from .local_palette_matcher import LocalPaletteMatcher
from .local_palette_shader_matcher import LocalPaletteShaderMatcher
from .mask_filler import MaskFiller
from .palette_matcher import PaletteMatcher

__all__ = [
    "LocalPaletteMatcher",
    "LocalPaletteShaderMatcher",
    "MaskFiller",
    "PaletteMatcher",
]
