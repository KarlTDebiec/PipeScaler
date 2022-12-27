#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for image sources."""
from __future__ import annotations

from abc import ABC, abstractmethod

from pipescaler.core.pipelines.image.pipe_image import PipeImage
from pipescaler.core.pipelines.source import Source


class ImageSource(Source, ABC):
    """Abstract base class for image sources."""

    @abstractmethod
    def __next__(self) -> PipeImage:
        """Return next objects."""
        raise NotImplementedError()
