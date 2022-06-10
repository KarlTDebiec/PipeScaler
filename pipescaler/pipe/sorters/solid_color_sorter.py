#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Sorts image based on presence of multiple colors."""
from __future__ import annotations

from logging import info

import numpy as np
from core import PipeImage, validate_mode

from pipescaler.common import validate_float, validate_int
from pipescaler.core.stages import Sorter


class SolidColorSorter(Sorter):
    """Sorts image based on presence of multiple colors."""

    def __init__(self, mean_threshold: float = 1, max_threshold: float = 10) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            mean_threshold: Sort as 'solid' if mean diff is below this threshold
            max_threshold: Sort as 'solid' if maximum diff is below this threshold
        """
        self.mean_threshold = validate_float(mean_threshold, 0, 255)
        self.max_threshold = validate_int(max_threshold, 0, 255)

    def __call__(self, pipe_image: PipeImage) -> str:
        image, mode = validate_mode(pipe_image.image, ("1", "L", "LA", "RGB", "RGBA"))
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
        """Outlets that flow out of stage."""
        return ("not_solid", "solid")
