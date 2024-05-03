#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for sorters."""
from __future__ import annotations

import re
from abc import ABC, abstractmethod
from inspect import cleandoc

from pipescaler.core.pipelines import PipeObject


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
        """Representation."""
        return f"{self.__class__.__name__}()"

    def __str__(self) -> str:
        """String representation."""
        return f"<{self.__class__.__name__}>"

    @property
    def outlets(self) -> tuple[str, ...]:
        """Outlets to which images may be sorted."""
        raise NotImplementedError()

    @classmethod
    def help_markdown(cls) -> str:
        """Short description of this class in markdown, with links."""
        if cls.__doc__:
            return re.split(r' *[.?!][\'")\]]* *', cleandoc(cls.__doc__))[0] + "."
        return ""
