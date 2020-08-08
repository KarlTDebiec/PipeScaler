#!/usr/bin/env python
#   pipescaler/sorters/__init__.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from __future__ import annotations

from typing import List

from pipescaler.sorters.ListSorter import ListSorter
from pipescaler.sorters.MipmapSorter import MipmapSorter
from pipescaler.sorters.RegexSorter import RegexSorter
from pipescaler.sorters.SizeSorter import SizeSorter
from pipescaler.sorters.TransparencySorter import TransparencySorter


##################################### ALL #####################################
__all__: List[str] = [
    "ListSorter",
    "MipmapSorter",
    "RegexSorter",
    "SizeSorter",
    "TransparencySorter"
]
