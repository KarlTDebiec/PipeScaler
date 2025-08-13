#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Sorts image based on presence and use of alpha channel."""

from __future__ import annotations

from logging import info

import numpy as np

from pipescaler.common.validation import val_int
from pipescaler.image.core.pipelines import ImageSorter, PipeImage
from pipescaler.image.core.validation import validate_image_and_convert_mode


class AlphaSorter(ImageSorter):
    """Sorts image based on presence and use of alpha channel."""

    def __init__(self, threshold: int = 255):
        """Validate configuration and initialize.

        Arguments:
            threshold: Sort as 'drop_alpha' if all pixels' alpha is above this threshold
        """
        self.threshold = val_int(threshold, min_value=0, max_value=255)

    def __call__(self, obj: PipeImage) -> str | None:
        """Get the outlet to which an image should be sorted.

        Arguments:
            obj: Image to sort
        Returns:
            Outlet to which image should be sorted
        """
        image, mode = validate_image_and_convert_mode(
            obj.image, ("1", "L", "LA", "RGB", "RGBA")
        )

        if mode in ("LA", "RGBA"):
            alpha_arr = np.array(image)[:, :, -1]
            if alpha_arr.min() >= self.threshold:
                outlet = "drop_alpha"
            else:
                outlet = "keep_alpha"
        else:
            outlet = "no_alpha"

        info(f"{self}: '{obj.location_name}' matches '{outlet}'")
        return outlet

    def __repr__(self) -> str:
        """Representation."""
        return f"{self.__class__.__name__}(threshold={self.threshold!r})"

    @property
    def outlets(self) -> tuple[str, ...]:
        """Outlets to which images may be sorted."""
        return "drop_alpha", "keep_alpha", "no_alpha"
