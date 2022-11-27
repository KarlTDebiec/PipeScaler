#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Segments that run images through operators."""
from pipescaler.core.pipelines.segments.operators.merger_segment import MergerSegment
from pipescaler.core.pipelines.segments.operators.processor_segment import (
    ProcessorSegment,
)
from pipescaler.core.pipelines.segments.operators.splitter_segment import (
    SplitterSegment,
)

__all__ = [
    "MergerSegment",
    "ProcessorSegment",
    "SplitterSegment",
]
