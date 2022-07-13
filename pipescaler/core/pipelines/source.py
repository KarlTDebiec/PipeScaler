#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for sources."""
import re
from abc import ABC, abstractmethod
from inspect import cleandoc


class Source(ABC):
    """Abstract base class for sources."""

    def __iter__(self):
        """Iterator for images."""
        return self

    @abstractmethod
    def __next__(self):
        """Return next image."""
        raise NotImplementedError()

    def __repr__(self):
        """Representation of source."""
        return f"<{self.__class__.__name__}>"

    @classmethod
    def help_markdown(cls) -> str:
        """Short description of this image operator in markdown, with links."""
        if cls.__doc__:
            return re.split(r' *[.?!][\'")\]]* *', cleandoc(cls.__doc__))[0] + "."
        return ""
