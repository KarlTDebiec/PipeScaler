#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for video pipeline segments."""

from __future__ import annotations

from abc import ABC

from pipescaler.core.pipelines.segment import Segment
from pipescaler.video.core.pipelines.pipe_video import PipeVideo


class VideoSegment(Segment[PipeVideo], ABC):
    """Abstract base class for video pipeline segments."""
