#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PipeScaler image splitter operators package."""

from __future__ import annotations

from pipescaler.image.operators.splitters.alpha_splitter import AlphaSplitter
from pipescaler.image.operators.splitters.normal_splitter import NormalSplitter

__all__ = [
    "AlphaSplitter",
    "NormalSplitter",
]
