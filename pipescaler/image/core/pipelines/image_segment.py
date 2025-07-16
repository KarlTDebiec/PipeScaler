#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for segments within image pipelines."""

from __future__ import annotations

from abc import ABC

from pipescaler.core.pipelines.segment import Segment
from pipescaler.image.core.pipelines.pipe_image import PipeImage


class ImageSegment(Segment[PipeImage], ABC):
    """Abstract base class for segments within image pipelines."""
