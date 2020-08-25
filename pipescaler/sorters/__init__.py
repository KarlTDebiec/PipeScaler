#!/usr/bin/env python
#   pipescaler/sorters/__init__.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from typing import List

from pipescaler.sorters.list_sorter import ListSorter
from pipescaler.sorters.regex_sorter import RegexSorter
from pipescaler.sorters.scale_sorter import ScaleSorter
from pipescaler.sorters.size_sorter import SizeSorter
from pipescaler.sorters.transparency_sorter import TransparencySorter

######################################### ALL ##########################################
__all__: List[str] = [
    "ListSorter",
    "ScaleSorter",
    "RegexSorter",
    "SizeSorter",
    "TransparencySorter",
]
