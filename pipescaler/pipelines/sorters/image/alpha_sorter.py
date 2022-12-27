#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Sorts image based on presence and use of alpha channel."""
from __future__ import annotations

from logging import info
from typing import Optional

import numpy as np

from pipescaler.common import validate_int
from pipescaler.core.image import validate_image_and_convert_mode
from pipescaler.core.pipelines.image import ImageSorter, PipeImage


class AlphaSorter(ImageSorter):
    """Sorts image based on presence and use of alpha channel."""

    def __init__(self, threshold: int = 255) -> None:
        """Validate configuration and initialize.

        Arguments:
            threshold: Sort as 'drop_alpha' if all pixels' alpha is above this threshold
        """
        self.threshold = validate_int(threshold, 0, 255)

    def __call__(self, pipe_object: PipeImage) -> Optional[str]:
        """Get the outlet to which an image should be sorted.

        Arguments:
            pipe_object: Image to sort
        Returns:
            Outlet to which image should be sorted
        """
        image, mode = validate_image_and_convert_mode(
            pipe_object.image, ("1", "L", "LA", "RGB", "RGBA")
        )

        if mode in ("LA", "RGBA"):
            alpha_array = np.array(image)[:, :, -1]
            if alpha_array.min() >= self.threshold:
                outlet = "drop_alpha"
            else:
                outlet = "keep_alpha"
        else:
            outlet = "no_alpha"

        info(f"{self}: '{pipe_object.location_name}' matches '{outlet}'")
        return outlet

    def __repr__(self) -> str:
        """Representation."""
        return f"{self.__class__.__name__}(threshold={self.threshold!r})"

    @property
    def outlets(self) -> tuple[str, ...]:
        """Outlets to which images may be sorted."""
        return ("drop_alpha", "keep_alpha", "no_alpha")
