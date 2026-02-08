#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for pipeline termini."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from inspect import cleandoc

from .pipe_object import PipeObject


class Terminus[T: PipeObject](ABC):
    """Abstract base class for pipeline termini."""

    @abstractmethod
    def __call__(self, input_obj: T):
        """Terminates image.

        Arguments:
            input_obj: Input object
        """
        raise NotImplementedError()

    def __repr__(self) -> str:
        """Representation."""
        return f"{self.__class__.__name__}()"

    def __str__(self) -> str:
        """String representation."""
        return f"<{self.__class__.__name__}>"

    @classmethod
    def help_markdown(cls) -> str:
        """Short description of this class in markdown, with links."""
        if cls.__doc__:
            return re.split(r' *[.?!][\'")\]]* *', cleandoc(cls.__doc__))[0] + "."
        return ""
