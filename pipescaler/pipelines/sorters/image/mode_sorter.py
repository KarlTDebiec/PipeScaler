#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Sorts image based on mode."""
from __future__ import annotations

from logging import info

from pipescaler.core.image import validate_image
from pipescaler.core.pipelines import PipeImage, Sorter


class ModeSorter(Sorter):
    """Sorts image based on mode.

    Supports pillow's modes 1, L, LA, RGB, and RGBA. Monochrome image mode is named 'M'
    rather than pillow's '1' in order to allow downstream outlets to be specified using
    keyword arguments,
    """

    def __call__(self, pipe_object: PipeImage) -> str:
        """Get the outlet to which an image should be sorted.

        Arguments:
            pipe_object: Image to sort
        Returns:
            Outlet to which image should be sorted
        """
        image = validate_image(pipe_object.image, ("1", "L", "LA", "RGB", "RGBA"))

        outlet = image.mode
        if outlet == "1":
            outlet = "M"

        info(f"{self}: '{pipe_object.location_name}' matches '{outlet}'")
        return outlet

    @property
    def outlets(self) -> tuple[str, ...]:
        """Outlets to which images may be sorted."""
        return ("M", "L", "LA", "RGB", "RGBA")
