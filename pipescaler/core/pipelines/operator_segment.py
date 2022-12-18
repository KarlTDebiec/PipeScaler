#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Segment that applies an Operator."""
from __future__ import annotations

from abc import ABC

from pipescaler.core.image import Operator
from pipescaler.core.pipelines.segment import Segment


class OperatorSegment(Segment, ABC):
    """Segment that applies an Operator."""

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
