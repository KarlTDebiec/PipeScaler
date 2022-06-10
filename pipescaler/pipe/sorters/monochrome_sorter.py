#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Sorts image based on presence and use of colors other than black and white."""
from __future__ import annotations

from logging import info

from pipescaler.common import validate_float
from pipescaler.core import PipeImage, is_monochrome, validate_mode
from pipescaler.core.stages import Sorter


class MonochromeSorter(Sorter):
    """Sorts image based on presence and use of colors other than black and white."""

    def __init__(self, mean_threshold: float = 0, max_threshold: float = 0) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            mean_threshold: Sort as 'drop_gray' if mean diff is below this threshold
            max_threshold: Sort as 'drop_gray' if maximum diff is below this threshold
        """
        self.mean_threshold = validate_float(mean_threshold, 0, 255)
        self.max_threshold = validate_float(max_threshold, 0, 255)

    def __call__(self, pipe_image: PipeImage) -> str:
        image, mode = validate_mode(pipe_image.image, ("1", "L"))

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
        """Outlets that flow out of stage."""
        return ("drop_gray", "keep_gray", "no_gray")
