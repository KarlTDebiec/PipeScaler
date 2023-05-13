#!/usr/bin/env python
#  Copyright 2020-2023 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for pipeline sources."""
from __future__ import annotations

import re
from abc import ABC, abstractmethod
from inspect import cleandoc

from pipescaler.core.pipelines.pipe_object import PipeObject


class Source(ABC):
    """Abstract base class for pipeline sources."""

    def __iter__(self) -> Source:
        """Iterator for objects."""
        return self

    @abstractmethod
    def __next__(self) -> PipeObject:
        """Return next object."""
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
