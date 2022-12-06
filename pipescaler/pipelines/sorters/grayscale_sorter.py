#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Sorts image based on presence and use of color channels."""
from __future__ import annotations

from logging import info

import numpy as np
from PIL import Image

from pipescaler.common import validate_float
from pipescaler.core.pipelines import PipeImage
from pipescaler.core.pipelines.sorter import Sorter
from pipescaler.core.validation import validate_image


class GrayscaleSorter(Sorter):
    """Sorts image based on presence and use of color channels."""

    def __init__(self, mean_threshold: float = 1, max_threshold: float = 10) -> None:
        """Validate configuration and initialize.

        Arguments:
            mean_threshold: Sort as 'drop_rgb' if mean diff between RGB and L images is
              below this threshold
            max_threshold: Sort as 'drop_rgb' if maximum diff between RGB and L images
              is below this threshold
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
        image = validate_image(pipe_image.image, ("L", "LA", "RGB", "RGBA"))

        if image.mode in ("RGB", "RGBA"):
            rgb_array = np.array(image)[:, :, :3]
            l_array = np.array(Image.fromarray(rgb_array).convert("L").convert("RGB"))
            diff = np.abs(rgb_array - l_array)
            if diff.mean() <= self.mean_threshold and diff.max() <= self.max_threshold:
                outlet = "drop_rgb"
            else:
                outlet = "keep_rgb"
        else:
            outlet = "no_rgb"

        info(f"{self}: {pipe_image.name} matches {outlet}")
        return outlet

    def __repr__(self):
        """Representation."""
        return (
            f"{self.__class__.__name__}("
            f"mean_threshold={self.mean_threshold},"
            f"max_threshold={self.max_threshold})"
        )

    @property
    def outlets(self) -> tuple[str, ...]:
        """Outlets to which images may be sorted."""
        return ("drop_rgb", "keep_rgb", "no_rgb")
