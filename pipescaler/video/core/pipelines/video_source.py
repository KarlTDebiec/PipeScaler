#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for video sources."""
from __future__ import annotations

from abc import ABC, abstractmethod

from pipescaler.core.pipelines.source import Source
from pipescaler.video.core.pipelines.pipe_video import PipeVideo


class VideoSource(Source, ABC):
    """Abstract base class for video sources."""

    @abstractmethod
    def __next__(self) -> PipeVideo:
        """Return next video."""
        raise NotImplementedError()
