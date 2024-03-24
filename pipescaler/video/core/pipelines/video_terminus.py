#  Copyright 2020-2023 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for video termini."""
from __future__ import annotations

from abc import ABC

from pipescaler.core.pipelines.terminus import Terminus
from pipescaler.video.core.pipelines.pipe_video import PipeVideo


class VideoTerminus(Terminus[PipeVideo], ABC):
    """Abstract base class for video termini."""
