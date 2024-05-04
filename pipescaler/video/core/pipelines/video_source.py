#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for video sources."""
from __future__ import annotations

from abc import ABC

from pipescaler.core.pipelines.source import Source
from pipescaler.video.core.pipelines.pipe_video import PipeVideo


class VideoSource(Source[PipeVideo], ABC):
    """Abstract base class for video sources."""
