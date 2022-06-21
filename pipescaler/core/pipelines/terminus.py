#!/usr/bin/env python
#  Copyright (C) 2022. Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for termini."""
from __future__ import annotations

from abc import ABC, abstractmethod

from pipescaler.core.pipelines.pipe_image import PipeImage


class Terminus(ABC):
    """Abstract base class for termini."""

    @abstractmethod
    def __call__(self, input_image: PipeImage) -> None:
        """Terminates image."""
        raise NotImplementedError

    def __repr__(self):
        """Representation."""
        return f"<{self.__class__.__name__}>"
