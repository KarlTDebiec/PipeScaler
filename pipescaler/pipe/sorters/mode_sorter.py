#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Sorts image based on mode."""
from __future__ import annotations

from logging import info

from pipescaler.core import PipeImage, validate_mode
from pipescaler.core.stages import Sorter


class ModeSorter(Sorter):
    """Sorts image based on mode.

    Supports pillow's modes 1, L, LA, RGB, and RGBA. Monochrome image mode is named 'M'
    rather than pillow's '1' in order to allow downstream outlets to be specified using
    keyword arguments,
    """

    def __call__(self, pipe_image: PipeImage) -> str:
        image, mode = validate_mode(pipe_image.image, ("1", "L", "LA", "RGB", "RGBA"))
        if mode == "1":
            mode = "M"
        info(f"{self}: '{pipe_image.name}' matches '{mode}'")
        return mode

    def __repr__(self):
        return "<ModeSorter>"

    @property
    def outlets(self) -> tuple[str, ...]:
        """Outlets that flow out of sorter."""
        return ("M", "L", "LA", "RGB", "RGBA")
