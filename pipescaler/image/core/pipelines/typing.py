#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Type hints for image pipelines."""

from __future__ import annotations

from collections.abc import Callable

from pipescaler.image.core.pipelines.image_segment import ImageSegment
from pipescaler.image.core.pipelines.pipe_image import PipeImage

type ImageSegmentLike = (ImageSegment | Callable[[PipeImage], tuple[PipeImage, ...]])
