#!/usr/bin/env python
#  Copyright 2020-2023 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for image sources."""
from __future__ import annotations

from abc import ABC, abstractmethod

from pipescaler.core.pipelines.source import Source
from pipescaler.image.core.pipelines.pipe_image import PipeImage


class ImageSource(Source, ABC):
    """Abstract base class for image sources."""

    @abstractmethod
    def __next__(self) -> PipeImage:
        """Return next image."""
        raise NotImplementedError()
