#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Type hints for video pipelines."""

from __future__ import annotations

from collections.abc import Callable

from .pipe_video import PipeVideo
from .video_segment import VideoSegment

type VideoSegmentLike = VideoSegment | Callable[[PipeVideo], tuple[PipeVideo, ...]]
