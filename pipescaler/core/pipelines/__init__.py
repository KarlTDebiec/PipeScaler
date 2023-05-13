#!/usr/bin/env python
#  Copyright 2020-2023 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PipeScaler general core pipelines package."""
from __future__ import annotations

from pipescaler.core.pipelines.checkpoint_manager_base import CheckpointManagerBase
from pipescaler.core.pipelines.checkpointed_segment import CheckpointedSegment
from pipescaler.core.pipelines.directory_source import DirectorySource
from pipescaler.core.pipelines.directory_terminus import DirectoryTerminus
from pipescaler.core.pipelines.exceptions import TerminusReached
from pipescaler.core.pipelines.pipe_object import PipeObject
from pipescaler.core.pipelines.segment import Segment
from pipescaler.core.pipelines.sorter import Sorter
from pipescaler.core.pipelines.source import Source
from pipescaler.core.pipelines.terminus import Terminus
from pipescaler.core.pipelines.typing import SegmentLike

__all__ = [
    "CheckpointManagerBase",
    "CheckpointedSegment",
    "DirectorySource",
    "DirectoryTerminus",
    "PipeObject",
    "Segment",
    "SegmentLike",
    "Sorter",
    "Source",
    "Terminus",
    "TerminusReached",
]
