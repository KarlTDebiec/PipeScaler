#!/usr/bin/env python
#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for ImageMerger command-line interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod
from inspect import cleandoc

from pipescaler.common import CommandLineInterface
from pipescaler.image.core.operators import ImageMerger


class ImageMergerCli(CommandLineInterface, ABC):
    """Abstract base class for ImageMerger command-line interfaces."""

    @classmethod
    def description(cls) -> str:
        """Long description of this tool displayed below usage."""
        return cleandoc(str(cls.merger().__doc__)) if cls.merger().__doc__ else ""

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser."""
        return cls.__name__.removesuffix("Cli").lower()

    @classmethod
    @abstractmethod
    def merger(cls) -> type[ImageMerger]:
        """Type of merger wrapped by command-line interface."""
        raise NotImplementedError()
