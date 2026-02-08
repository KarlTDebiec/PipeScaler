#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PipeScaler general core pipelines package.

This module may import from: common

Hierarchy within module:
* exceptions / typing / pipe_object
* source / terminus / segment / sorter
* checkpoint_manager_base / checkpointed_segment
* directory_source / directory_terminus
"""

from __future__ import annotations

from .checkpoint_manager_base import CheckpointManagerBase
from .checkpointed_segment import CheckpointedSegment
from .directory_source import DirectorySource
from .directory_terminus import DirectoryTerminus
from .exceptions import TerminusReached
from .pipe_object import PipeObject
from .segment import Segment
from .sorter import Sorter
from .source import Source
from .terminus import Terminus
from .typing import SegmentLike

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
