#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for utilities."""

from __future__ import annotations

from abc import ABC, abstractmethod
from inspect import cleandoc
from typing import Any


class Utility(ABC):
    """Abstract base class for utilities."""

    @classmethod
    @abstractmethod
    def run(cls, **kwargs: Any) -> Any:
        """Execute utility behavior.

        Arguments:
            **kwargs: keyword arguments used by utility implementation
        Returns:
            output produced by utility implementation
        """
        raise NotImplementedError()

    @classmethod
    def help_markdown(cls) -> str:
        """Short description of this utility in markdown, with links."""
        if cls.__doc__:
            return cleandoc(cls.__doc__).split(". ", maxsplit=1)[0]
        return ""
