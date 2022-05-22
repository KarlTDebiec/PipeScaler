#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Abstract base classes for stages."""
from __future__ import annotations

from pipescaler.core.stages.merger import Merger
from pipescaler.core.stages.processor import Processor
from pipescaler.core.stages.sorter import Sorter
from pipescaler.core.stages.source import Source
from pipescaler.core.stages.splitter import Splitter
from pipescaler.core.stages.terminus import Terminus

__all__: list[str] = [
    "Merger",
    "Processor",
    "Sorter",
    "Source",
    "Splitter",
    "Terminus",
]
