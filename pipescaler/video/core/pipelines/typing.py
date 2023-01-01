#  Copyright 2020-2023 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Type hints for video pipelines."""
from __future__ import annotations

from typing import Callable, Union

from pipescaler.video.core.pipelines.pipe_video import PipeVideo
from pipescaler.video.core.pipelines.video_segment import VideoSegment

VideoSegmentLike = Union[VideoSegment, Callable[[PipeVideo], tuple[PipeVideo, ...]]]
