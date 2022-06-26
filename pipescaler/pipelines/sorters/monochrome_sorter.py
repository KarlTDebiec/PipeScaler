#!/usr/bin/env python
#  Copyright (C) 2020-2022. Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Sorts image based on presence and use of colors other than black and white."""
from __future__ import annotations

from logging import info

from pipescaler.common import validate_float
from pipescaler.core.image import is_monochrome
from pipescaler.core.pipelines import PipeImage
from pipescaler.core.pipelines.sorter import Sorter
from pipescaler.core.validation import validate_image


class MonochromeSorter(Sorter):
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

    def __call__(self, pipe_image: PipeImage) -> str:
        """Get the outlet to which an image should be sorted.

        Arguments:
            pipe_image: Image to sort
        Returns:
            Outlet to which image should be sorted
        """
        image = validate_image(pipe_image.image, ("1", "L"))

        if image.mode == "L":
            if is_monochrome(image):
                outlet = "drop_gray"
            else:
                outlet = "keep_gray"
        else:
            outlet = "no_gray"

        info(f"{self}: {pipe_image.name} matches {outlet}")
        return outlet

    @property
    def outlets(self) -> tuple[str, ...]:
        """Outlets to which images may be sorted."""
        return ("drop_gray", "keep_gray", "no_gray")
