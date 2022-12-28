#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Image segments"""
from __future__ import annotations

from pipescaler.pipelines.segments.image.merger_segment import MergerSegment
from pipescaler.pipelines.segments.image.processor_segment import ProcessorSegment
from pipescaler.pipelines.segments.image.runner_segment import RunnerSegment
from pipescaler.pipelines.segments.image.splitter_segment import SplitterSegment

__all__ = [
    "MergerSegment",
    "ProcessorSegment",
    "RunnerSegment",
    "SplitterSegment",
]
