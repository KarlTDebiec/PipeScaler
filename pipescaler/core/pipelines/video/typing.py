#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Type hints for video pipelines."""
from __future__ import annotations

from typing import Callable, Union

from pipescaler.core.pipelines.video.video_segment import PipeVideo, VideoSegment

VideoSegmentLike = Union[VideoSegment, Callable[[PipeVideo], tuple[PipeVideo, ...]]]
