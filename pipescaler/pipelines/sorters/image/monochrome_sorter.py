#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Sorts image based on presence and use of colors other than black and white."""
from __future__ import annotations

from logging import info
from typing import Optional

from pipescaler.common import validate_float
from pipescaler.core.image import is_monochrome, validate_image
from pipescaler.core.pipelines.image import ImageSorter, PipeImage


class MonochromeSorter(ImageSorter):
    """Sorts image based on presence and use of colors other than black and white."""

    def __init__(self, mean_threshold: float = 0, max_threshold: float = 0) -> None:
        """Validate configuration and initialize.

        Arguments:
            mean_threshold: Sort as 'drop_gray' if mean diff between L and 1 images is
              below this threshold
            max_threshold: Sort as 'drop_gray' if maximum diff between L and 1 images is
             below this threshold
        """
        self.mean_threshold = validate_float(mean_threshold, 0, 255)
        self.max_threshold = validate_float(max_threshold, 0, 255)

    def __call__(self, pipe_object: PipeImage) -> Optional[str]:
        """Get the outlet to which an image should be sorted.

        Arguments:
            pipe_object: Image to sort
        Returns:
            Outlet to which image should be sorted
        """
        image = validate_image(pipe_object.image, ("1", "L"))

        if image.mode == "L":
            if is_monochrome(image):
                outlet = "drop_gray"
            else:
                outlet = "keep_gray"
        else:
            outlet = "no_gray"

        info(f"{self}: '{pipe_object.location_name}' matches {outlet}")
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
        return ("drop_gray", "keep_gray", "no_gray")
