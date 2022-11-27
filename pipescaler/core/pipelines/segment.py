#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Segment within a pipeline."""
from abc import ABC, abstractmethod

from pipescaler.core.pipelines.pipe_image import PipeImage


class Segment(ABC):
    """Segment within a pipeline."""

    @abstractmethod
    def __call__(self, *inputs: PipeImage) -> tuple[PipeImage]:
        """Receive input images and returns output images.

        Arguments:
            inputs: Input images
        Returns:
            Output images, within a tuple even if only one
        """
        raise NotImplementedError()
