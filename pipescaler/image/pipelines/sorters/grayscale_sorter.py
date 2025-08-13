#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Sorts image based on presence and use of color channels."""

from __future__ import annotations

from logging import info

import numpy as np
from PIL import Image

from pipescaler.common.validation import val_float
from pipescaler.image.core.pipelines import ImageSorter, PipeImage
from pipescaler.image.core.validation import validate_image


class GrayscaleSorter(ImageSorter):
    """Sorts image based on presence and use of color channels."""

    def __init__(self, mean_threshold: float = 1, max_threshold: float = 10):
        """Validate configuration and initialize.

        Arguments:
            mean_threshold: Sort as 'drop_rgb' if mean diff between RGB and L images is
              below this threshold
            max_threshold: Sort as 'drop_rgb' if maximum diff between RGB and L images
              is below this threshold
        """
        self.mean_threshold = val_float(mean_threshold, min_value=0, max_value=255)
        self.max_threshold = val_float(max_threshold, min_value=0, max_value=255)

    def __call__(self, obj: PipeImage) -> str | None:
        """Get the outlet to which an image should be sorted.

        Arguments:
            obj: Image to sort
        Returns:
            Outlet to which image should be sorted
        """
        img = validate_image(obj.image, ("L", "LA", "RGB", "RGBA"))

        if img.mode in ("RGB", "RGBA"):
            rgb_arr = np.array(img)[:, :, :3]
            l_arr = np.array(Image.fromarray(rgb_arr).convert("L").convert("RGB"))
            diff = np.abs(rgb_arr - l_arr)
            if diff.mean() <= self.mean_threshold and diff.max() <= self.max_threshold:
                outlet = "drop_rgb"
            else:
                outlet = "keep_rgb"
        else:
            outlet = "no_rgb"

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
        return "drop_rgb", "keep_rgb", "no_rgb"
