#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for image operators."""

from __future__ import annotations

import re
from abc import ABC
from inspect import cleandoc
from typing import Any


class ImageOperator(ABC):
    """Abstract base class for image operators."""

    def __init__(self, **kwargs: Any) -> None:
        """Initializes an image operator."""

    def __repr__(self) -> str:
        """Representation."""
        return f"{self.__class__.__name__}()"

    def __str__(self) -> str:
        """String representation."""
        return f"<{self.__class__.__name__}>"

    @classmethod
    def help_markdown(cls) -> str:
        """Short description of this image operator in markdown, with links."""
        if cls.__doc__:
            return re.split(r' *[.?!][\'")\]]* *', cleandoc(cls.__doc__))[0] + "."
        return ""

    @classmethod
    def inputs(cls) -> dict[str, tuple[str, ...]]:
        """Inputs to this operator."""
        raise NotImplementedError()

    @classmethod
    def outputs(cls) -> dict[str, tuple[str, ...]]:
        """Outputs of this operator."""
        raise NotImplementedError()
