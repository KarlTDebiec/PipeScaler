#  Copyright 2020-2023 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for video pipeline segments."""
from __future__ import annotations

from abc import ABC, abstractmethod

from pipescaler.core.pipelines.segment import Segment
from pipescaler.video.core.pipelines.pipe_video import PipeVideo


class VideoSegment(Segment, ABC):
    """Abstract base class for video pipeline segments."""

    @abstractmethod
    def __call__(self, *inputs: PipeVideo) -> tuple[PipeVideo, ...]:
        """Receive input videos and returns output videos.

        Arguments:
            inputs: Input videos
        Returns:
            Output videos, within a tuple even if only one
        """
        raise NotImplementedError()
