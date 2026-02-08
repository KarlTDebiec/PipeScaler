#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PipeScaler image splitter operators package.

This module may import from: common, core, image.core, image.core.operators

Hierarchy within module:
* alpha_splitter / normal_splitter
"""

from __future__ import annotations

from .alpha_splitter import AlphaSplitter
from .normal_splitter import NormalSplitter

__all__ = [
    "AlphaSplitter",
    "NormalSplitter",
]
