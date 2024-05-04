#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for segments that apply ImageOperators."""
from __future__ import annotations

from abc import ABC, abstractmethod

from pipescaler.image.core import ImageOperator
from pipescaler.image.core.pipelines.image_segment import ImageSegment
from pipescaler.image.core.pipelines.pipe_image import PipeImage


class ImageOperatorSegment(ImageSegment, ABC):
    """Abstract base class for segments that apply ImageOperators."""

    operator: ImageOperator

    def __init__(self, operator: ImageOperator) -> None:
        """Initialize.

        Arguments:
            operator: Operator to apply
        """
        self.operator = operator
        """Operator to apply"""

    @abstractmethod
    def __call__(self, *inputs: PipeImage) -> tuple[PipeImage, ...]:
        """Process an image.

        Arguments:
            inputs: Input image, within a tuple for consistency with other Segments
        Returns:
            Output image, within a tuple for consistency with other Segments
        """
        raise NotImplementedError()

    def __repr__(self) -> str:
        """Representation."""
        return f"{self.__class__.__name__}(operator={self.operator!r})"
