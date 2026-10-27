#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for sorters."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from inspect import cleandoc

from .pipe_object import PipeObject

__all__ = ["Sorter"]


class Sorter[T: PipeObject](ABC):
    """Abstract base class for sorters."""

    @abstractmethod
    def __call__(self, obj: T) -> str | None:
        """Get the outlet to which an object should be sorted.

        Arguments:
            obj: Object to sort
        Returns:
            Outlet to which object should be sorted
        """
        raise NotImplementedError()

    def __repr__(self) -> str:
        """Representation.

        Returns:
            string representation of this object
        """
        return f"{self.__class__.__name__}()"

    def __str__(self) -> str:
        """String representation.

        Returns:
            display string for this object
        """
        return f"<{self.__class__.__name__}>"

    @property
    def outlets(self) -> tuple[str, ...]:
        """Outlets to which images may be sorted.

        Raises:
            NotImplementedError: if the subclass does not implement this operation
        """
        raise NotImplementedError()

    @classmethod
    def help_markdown(cls) -> str:
        """Short description of this class in markdown, with links.

        Returns:
            Markdown help describing this component
        """
        if cls.__doc__:
            return re.split(r' *[.?!][\'")\]]* *', cleandoc(cls.__doc__))[0] + "."
        return ""
