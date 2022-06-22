#!/usr/bin/env python
#  Copyright (C) 2020-2022. Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for sorters."""
from __future__ import annotations

import re
from abc import ABC, abstractmethod
from inspect import cleandoc

from pipescaler.core.pipelines.pipe_image import PipeImage


class Sorter(ABC):
    """Base class for sorters."""

    @abstractmethod
    def __call__(self, pipe_image: PipeImage) -> str:
        """Get the outlet to which an image should be sorted.

        Arguments:
            pipe_image: Image to sort
        Returns:
            Outlet to which image should be sorted
        """
        raise NotImplementedError()

    def __repr__(self):
        """Representation of sorter."""
        return f"<{self.__class__.__name__}>"

    @property
    @abstractmethod
    def outlets(self) -> tuple[str, ...]:
        """Outlets that flow out of sorter."""
        raise NotImplementedError()

    @classmethod
    @property
    def help_markdown(cls) -> str:
        """Short description of this image operator in markdown, with links."""
        if cls.__doc__:
            return re.split(r' *[\.\?!][\'"\)\]]* *', cleandoc(cls.__doc__))[0] + "."
        return ""
