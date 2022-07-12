#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Splitter image operators."""
from __future__ import annotations

from pipescaler.image.splitters.alpha_splitter import AlphaSplitter
from pipescaler.image.splitters.normal_splitter import NormalSplitter

__all__: list[str] = [
    "AlphaSplitter",
    "NormalSplitter",
]
