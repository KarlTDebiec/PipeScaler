#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Base class for video sorters."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from pipescaler.core.pipelines import PipeVideo
from pipescaler.core.pipelines.sorter import Sorter


class VideoSorter(Sorter, ABC):
    """Base class for video sorters."""

    @abstractmethod
    def __call__(self, pipe_video: PipeVideo) -> Optional[str]:
        """Get the outlet to which a video should be sorted.

        Arguments:
            pipe_video: Video to sort
        Returns:
            Outlet to which video should be sorted
        """
        raise NotImplementedError()
