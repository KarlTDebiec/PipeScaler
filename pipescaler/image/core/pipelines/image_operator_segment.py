#  Copyright 2020-2023 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for segments that apply image operators."""
from __future__ import annotations

from abc import ABC

from pipescaler.image.core import ImageOperator
from pipescaler.image.core.pipelines.image_segment import ImageSegment


class ImageOperatorSegment(ImageSegment, ABC):
    """Abstract base class for segments that apply image operators."""

    operator: ImageOperator

    def __init__(self, operator: ImageOperator) -> None:
        """Initialize.

        Arguments:
            operator: Operator to apply
        """
        self.operator = operator
        """Operator to apply"""

    def __repr__(self) -> str:
        """Representation."""
        return f"{self.__class__.__name__}(operator={self.operator!r})"
