#!/usr/bin/env python
#  Copyright 2020-2023 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for image sorters."""
from __future__ import annotations

from abc import ABC, abstractmethod

from pipescaler.core.pipelines.sorter import Sorter
from pipescaler.image.core.pipelines.pipe_image import PipeImage


class ImageSorter(Sorter, ABC):
    """Abstract base class for image sorters."""

    @abstractmethod
    def __call__(self, pipe_image: PipeImage) -> str | None:
        """Get the outlet to which an image should be sorted.

        Arguments:
            pipe_image: Image to sort
        Returns:
            Outlet to which image should be sorted
        """
        raise NotImplementedError()
