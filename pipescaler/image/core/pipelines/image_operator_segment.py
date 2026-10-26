#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for segments that apply ImageOperators."""

from __future__ import annotations

from abc import ABC, abstractmethod

from pipescaler.image.core.image_operator import ImageOperator
from pipescaler.image.core.pipelines.image_segment import ImageSegment
from pipescaler.image.core.pipelines.pipe_image import PipeImage

__all__ = ["ImageOperatorSegment"]


class ImageOperatorSegment[T: ImageOperator](ImageSegment, ABC):
    """Abstract base class for segments that apply ImageOperators."""

    operator: T
    """Operator to apply."""

    def __init__(self, operator: T):
        """Initialize.

        Arguments:
            operator: Operator to apply
        """
        self.operator = operator
        """Operator to apply"""

    @abstractmethod
    def __call__(self, *input_objs: PipeImage) -> tuple[PipeImage, ...]:
        """Process an image.

        Arguments:
            *input_objs: Input image, within a tuple for consistency with other Segments
        Returns:
            Output image, within a tuple for consistency with other Segments
        """
        raise NotImplementedError()

    def __repr__(self) -> str:
        """Representation.

        Returns:
            string representation of this object
        """
        return f"{self.__class__.__name__}(operator={self.operator!r})"
