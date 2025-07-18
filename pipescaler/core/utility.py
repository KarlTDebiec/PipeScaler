#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for utilities."""

from __future__ import annotations

from abc import ABC
from inspect import cleandoc


class Utility(ABC):
    """Abstract base class for utilities."""

    @classmethod
    def help_markdown(cls) -> str:
        """Short description of this utility in markdown, with links."""
        if cls.__doc__:
            return cleandoc(cls.__doc__).split(". ", maxsplit=1)[0]
        return ""
