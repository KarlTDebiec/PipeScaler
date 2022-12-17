#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Pipelines."""
from __future__ import annotations

from pipescaler.core.pipelines.checkpoint_manager_base import CheckpointManagerBase
from pipescaler.core.pipelines.checkpointed_segment import CheckpointedSegment
from pipescaler.core.pipelines.exceptions import TerminusReached
from pipescaler.core.pipelines.operator_segment import OperatorSegment
from pipescaler.core.pipelines.pipe_image import PipeImage
from pipescaler.core.pipelines.pipe_object import PipeObject
from pipescaler.core.pipelines.pipe_video import PipeVideo
from pipescaler.core.pipelines.segment import Segment
from pipescaler.core.pipelines.sorter import Sorter
from pipescaler.core.pipelines.source import Source
from pipescaler.core.pipelines.terminus import Terminus
from pipescaler.core.pipelines.typing import SegmentLike

__all__ = [
    "CheckpointManagerBase",
    "CheckpointedSegment",
    "OperatorSegment",
    "PipeImage",
    "PipeObject",
    "PipeVideo",
    "Segment",
    "SegmentLike",
    "Sorter",
    "Source",
    "Terminus",
    "TerminusReached",
]
