#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PipeScaler image utilities package.

This module may import from: common, core, image.core

Package hierarchy (modules may import from any above):
* local_palette_matcher / mask_shader_filler / palette_matcher
* palette_shader_matcher / mask_filler
"""

from __future__ import annotations

from .local_palette_matcher import LocalPaletteMatcher
from .mask_filler import MaskFiller
from .mask_shader_filler import MaskShaderFiller
from .palette_matcher import PaletteMatcher
from .palette_shader_matcher import PaletteShaderMatcher

__all__ = [
    "LocalPaletteMatcher",
    "MaskFiller",
    "MaskShaderFiller",
    "PaletteMatcher",
    "PaletteShaderMatcher",
]
