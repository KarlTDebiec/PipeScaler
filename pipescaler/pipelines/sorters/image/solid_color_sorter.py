#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Sorts image based on whether their entire canvas is a solid color."""
from __future__ import annotations

from logging import info
from typing import Optional

import numpy as np

from pipescaler.common import validate_int
from pipescaler.core.image import validate_image
from pipescaler.core.pipelines import PipeImage, Sorter


class SolidColorSorter(Sorter):
    """Sorts images based on whether their entire canvas is a solid color."""

    def __init__(self, mean_threshold: int = 1, max_threshold: int = 10) -> None:
        """Validate configuration and initialize.

        Arguments:
            mean_threshold: Sort as 'solid' if mean diff between image and its average
              color is below this threshold
            max_threshold: Sort as 'solid' if maximum diff between image and its average
              color is below this threshold
        """
        self.mean_threshold = validate_int(mean_threshold, 0, 255)
        self.max_threshold = validate_int(max_threshold, 0, 255)

    def __call__(self, pipe_object: PipeImage) -> Optional[str]:
        """Get the outlet to which an image should be sorted.

        Arguments:
            pipe_object: Image to sort
        Returns:
            Outlet to which image should be sorted
        """
        image = validate_image(pipe_object.image, ("1", "L", "LA", "RGB", "RGBA"))
        array = np.array(image)

        if image.mode in ("L", "LA", "RGB", "RGBA"):
            if image.mode in ("LA", "RGB", "RGBA"):
                diff = np.abs(array - array.mean(axis=(0, 1)))
            else:
                diff = np.abs(array - array.mean())
            if diff.mean() <= self.mean_threshold and diff.max() <= self.max_threshold:
                outlet = "solid"
            else:
                outlet = "not_solid"
        else:
            if np.all(np.abs(array - array.mean()) == 0):
                outlet = "solid"
            else:
                outlet = "not_solid"

        info(f"{self}: '{pipe_object.location_name}' matches '{outlet}'")
        return outlet

    def __repr__(self) -> str:
        """Representation."""
        return (
            f"{self.__class__.__name__}("
            f"mean_threshold={self.mean_threshold!r}, "
            f"max_threshold={self.max_threshold!r})"
        )

    @property
    def outlets(self) -> tuple[str, ...]:
        """Outlets to which images may be sorted."""
        return ("not_solid", "solid")
