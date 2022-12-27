#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for segments within video pipelines."""
from __future__ import annotations

from abc import ABC, abstractmethod

from pipescaler.core.pipelines.segment import Segment
from pipescaler.core.pipelines.video.pipe_video import PipeVideo


class VideoSegment(Segment, ABC):
    """Abstract base class for segments within video pipelines."""

    @abstractmethod
    def __call__(self, *inputs: PipeVideo) -> tuple[PipeVideo, ...]:
        """Receive input videos and returns output videos.

        Arguments:
            inputs: Input videos
        Returns:
            Output videos, within a tuple even if only one
        """
        raise NotImplementedError()
