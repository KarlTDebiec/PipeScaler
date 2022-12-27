#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Type hints for image pipelines."""
from __future__ import annotations

from typing import Callable, Union

from pipescaler.core.pipelines.image.image_segment import ImageSegment
from pipescaler.core.pipelines.image.pipe_image import PipeImage

ImageSegmentLike = Union[ImageSegment, Callable[[PipeImage], tuple[PipeImage, ...]]]
