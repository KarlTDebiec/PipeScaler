#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for termini."""
from __future__ import annotations

import re
from abc import ABC, abstractmethod
from inspect import cleandoc

from pipescaler.core.pipelines.pipe_image import PipeImage


class Terminus(ABC):
    """Abstract base class for termini."""

    @abstractmethod
    def __call__(self, input_image: PipeImage) -> None:
        """Terminates image."""
        raise NotImplementedError

    def __repr__(self):
        """Representation of terminus."""
        return f"<{self.__class__.__name__}>"

    @classmethod
    def help_markdown(cls) -> str:
        """Short description of this class in markdown, with links."""
        if cls.__doc__:
            return re.split(r' *[.?!][\'")\]]* *', cleandoc(cls.__doc__))[0] + "."
        return ""
