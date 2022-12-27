#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for segments within image pipelines."""
from __future__ import annotations

from abc import ABC, abstractmethod

from pipescaler.core.pipelines.image.pipe_image import PipeImage
from pipescaler.core.pipelines.segment import Segment


class ImageSegment(Segment, ABC):
    """Abstract base class for segments within image pipelines."""

    @abstractmethod
    def __call__(self, *inputs: PipeImage) -> tuple[PipeImage, ...]:
        """Receive input images and returns output images.

        Arguments:
            inputs: Input images
        Returns:
            Output images, within a tuple even if only one
        """
        raise NotImplementedError()
