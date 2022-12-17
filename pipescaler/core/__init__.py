#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Core."""
from __future__ import annotations

from pipescaler.core.enums import AlphaMode, MaskFillMode, PaletteMatchMode
from pipescaler.core.files import read_yaml
from pipescaler.core.runner import Runner
from pipescaler.core.sorting import basic_sort, citra_sort, dolphin_sort, texmod_sort
from pipescaler.core.typing import RunnerLike
from pipescaler.core.utility import Utility

__all__ = [
    "AlphaMode",
    "MaskFillMode",
    "PaletteMatchMode",
    "Runner",
    "RunnerLike",
    "Utility",
    "basic_sort",
    "citra_sort",
    "dolphin_sort",
    "read_yaml",
    "texmod_sort",
]
