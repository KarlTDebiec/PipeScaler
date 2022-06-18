#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for sorters."""
from __future__ import annotations

from abc import ABC, abstractmethod

from pipescaler.core.pipelines.pipe_image import PipeImage


class Sorter(ABC):
    """Base class for sorters."""

    @abstractmethod
    def __call__(self, pipe_image: PipeImage) -> str:
        raise NotImplementedError()

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    @property
    @abstractmethod
    def outlets(self) -> tuple[str, ...]:
        """Outlets that flow out of sorter."""
        raise NotImplementedError()
