#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for segments that apply image operators."""
from __future__ import annotations

from abc import ABC

from pipescaler.core.image import Operator
from pipescaler.core.pipelines.image.image_segment import ImageSegment


class OperatorSegment(ImageSegment, ABC):
    """Abstract base class for segments that apply image operators."""

    operator: Operator

    def __init__(self, operator: Operator) -> None:
        """Initialize.

        Arguments:
            operator: Operator to apply
        """
        self.operator = operator
        """Operator to apply"""

    def __repr__(self) -> str:
        """Representation."""
        return f"{self.__class__.__name__}(operator={self.operator!r})"
