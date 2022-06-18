#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Sorts image based on canvas size."""
from __future__ import annotations

from logging import info

from pipescaler.common import validate_int
from pipescaler.core.pipelines import PipeImage
from pipescaler.core.pipelines.sorter import Sorter


class SizeSorter(Sorter):
    """Sorts image based on canvas size."""

    def __init__(self, cutoff: int = 32) -> None:
        self.cutoff = validate_int(cutoff, min_value=1)

    def __call__(self, pipe_image: PipeImage) -> str:
        image = pipe_image.image

        if image.size[0] < self.cutoff or image.size[1] < self.cutoff:
            outlet = "less_than"
        else:
            outlet = "greater_than_or_equal_to"
        info(f"{self}: '{pipe_image.name}' matches '{outlet}'")
        return outlet

    @property
    def outlets(self) -> tuple[str, ...]:
        """Outlets that flow out of stage."""
        return ("less_than", "greater_than_or_equal_to")
