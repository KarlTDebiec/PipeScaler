#  Copyright 2020-2023 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Sorts image based on whether their entire canvas is a solid color."""
from __future__ import annotations

from logging import info

import numpy as np

from pipescaler.common import validate_int
from pipescaler.image.core import validate_image
from pipescaler.image.core.pipelines import ImageSorter, PipeImage


class SolidColorSorter(ImageSorter):
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

    def __call__(self, obj: PipeImage) -> str | None:
        """Get the outlet to which an image should be sorted.

        Arguments:
            obj: Image to sort
        Returns:
            Outlet to which image should be sorted
        """
        image = validate_image(obj.image, ("1", "L", "LA", "RGB", "RGBA"))
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

        info(f"{self}: '{obj.location_name}' matches '{outlet}'")
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
