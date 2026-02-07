#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PipeScaler image splitter operators package."""

from __future__ import annotations

from .alpha_splitter import AlphaSplitter
from .normal_splitter import NormalSplitter

__all__ = [
    "AlphaSplitter",
    "NormalSplitter",
]
