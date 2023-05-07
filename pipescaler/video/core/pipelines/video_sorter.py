#!/usr/bin/env python
#  Copyright 2020-2023 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for video sorters."""
from __future__ import annotations

from abc import ABC, abstractmethod

from pipescaler.core.pipelines.sorter import Sorter
from pipescaler.video.core.pipelines.pipe_video import PipeVideo


class VideoSorter(Sorter, ABC):
    """Abstract base class for video sorters."""

    @abstractmethod
    def __call__(self, pipe_video: PipeVideo) -> str | None:
        """Get the outlet to which a video should be sorted.

        Arguments:
            pipe_video: Video to sort
        Returns:
            Outlet to which video should be sorted
        """
        raise NotImplementedError()
