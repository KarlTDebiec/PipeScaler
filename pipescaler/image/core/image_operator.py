#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for image operators."""

from __future__ import annotations

import re
from abc import ABC
from inspect import cleandoc
from typing import Any

from .typing import ImageMode

__all__ = ["ImageOperator"]


class ImageOperator(ABC):
    """Abstract base class for image operators."""

    def __init__(self, **kwargs: Any):
        """Initializes an image operator.

        Arguments:
            **kwargs: additional options forwarded to the selected implementation
        """

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

    @classmethod
    def help_markdown(cls) -> str:
        """Short description of this image operator in markdown, with links.

        Returns:
            Markdown help describing this component
        """
        if cls.__doc__:
            return re.split(r' *[.?!][\'")\]]* *', cleandoc(cls.__doc__))[0] + "."
        return ""

    @classmethod
    def inputs(cls) -> dict[str, tuple[ImageMode, ...]]:
        """Inputs to this operator.

        Returns:
            mapping of input names to their supported image modes
        Raises:
            NotImplementedError: if the subclass does not implement this operation
        """
        raise NotImplementedError()

    @classmethod
    def outputs(cls) -> dict[str, tuple[ImageMode, ...]]:
        """Outputs of this operator.

        Returns:
            mapping of output names to their supported image modes
        Raises:
            NotImplementedError: if the subclass does not implement this operation
        """
        raise NotImplementedError()
