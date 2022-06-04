#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Abstract base classes for pipe stages."""
from __future__ import annotations

from pipescaler.core.pipe.merger_pipe import MergerPipe
from pipescaler.core.pipe.processor_pipe import ProcessorPipe
from pipescaler.core.pipe.sorter_pipe import SorterPipe
from pipescaler.core.pipe.source_pipe import SourcePipe
from pipescaler.core.pipe.splitter_pipe import SplitterPipe
from pipescaler.core.pipe.terminus_pipe import TerminusPipe

__all__: list[str] = [
    "MergerPipe",
    "ProcessorPipe",
    "SorterPipe",
    "SourcePipe",
    "SplitterPipe",
    "TerminusPipe",
]
