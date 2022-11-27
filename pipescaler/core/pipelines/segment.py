#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Segment within a pipeline."""
from abc import ABC, abstractmethod
from typing import Sequence, Union

from pipescaler.core.pipelines.pipe_image import PipeImage


class Segment(ABC):
    """Segment within a pipeline."""

    @abstractmethod
    def __call__(self, *inputs: PipeImage) -> Union[PipeImage, Sequence[PipeImage]]:
        """Receives input images and returns output images.

        Arguments:
            inputs: Input image(s)
        Returns:
            Output image(s)
        """
        raise NotImplementedError()
