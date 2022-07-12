#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Sorts image based on whether their entire canvas is a solid color."""
from __future__ import annotations

from logging import info

import numpy as np

from pipescaler.common import validate_float, validate_int
from pipescaler.core.pipelines import PipeImage
from pipescaler.core.pipelines.sorter import Sorter
from pipescaler.core.validation import validate_image


class SolidColorSorter(Sorter):
    """Sorts image based on whether their entire canvas is a solid color."""

    def __init__(self, mean_threshold: float = 1, max_threshold: float = 10) -> None:
        """Validate configuration and initialize.

        Arguments:
            mean_threshold: Sort as 'solid' if mean diff between image and its average
              color is below this threshold
            max_threshold: Sort as 'solid' if maximum diff between image and its average
              color is below this threshold
        """
        self.mean_threshold = validate_float(mean_threshold, 0, 255)
        self.max_threshold = validate_int(max_threshold, 0, 255)

    def __call__(self, pipe_image: PipeImage) -> str:
        """Get the outlet to which an image should be sorted.

        Arguments:
            pipe_image: Image to sort
        Returns:
            Outlet to which image should be sorted
        """
        image = validate_image(pipe_image.image, ("1", "L", "LA", "RGB", "RGBA"))
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

        info(f"{self}: {pipe_image.name} matches {outlet}")
        return outlet

    @property
    def outlets(self) -> tuple[str, ...]:
        """Outlets to which images may be sorted."""
        return ("not_solid", "solid")
