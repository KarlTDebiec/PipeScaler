#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for pipeline segments."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .pipe_object import PipeObject


class Segment[T: PipeObject](ABC):
    """Abstract base class for pipeline segments."""

    @abstractmethod
    def __call__(self, *input_objs: T) -> tuple[T, ...]:
        """Receive input objects and returns output objects.

        Arguments:
            input_objs: Input objects
        Returns:
            Output objects, within a tuple even if only one
        """
        raise NotImplementedError()

    def __repr__(self) -> str:
        """Representation."""
        return f"{self.__class__.__name__}()"

    def __str__(self) -> str:
        """String representation."""
        return f"<{self.__class__.__name__}>"
