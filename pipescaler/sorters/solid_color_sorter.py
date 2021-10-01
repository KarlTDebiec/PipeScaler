#!/usr/bin/env python
#   pipescaler/sorters/solid_color_sorter.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
from __future__ import annotations

from logging import info
from typing import Any, List

import numpy as np

from pipescaler.common import validate_float, validate_int
from pipescaler.core import Sorter, validate_image


class SolidColorSorter(Sorter):
    """Sorts image based on presence of multiple colors."""

    def __init__(
        self, mean_threshold: float = 1, max_threshold: float = 10, **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)

        # Store configuration
        self.mean_threshold = validate_float(mean_threshold, 0, 255)
        self.max_threshold = validate_int(max_threshold, 0, 255)

    def __call__(self, infile: str) -> str:

        # Read image
        image = validate_image(infile, ["L", "LA", "RGB", "RGBA"])
        datum = np.array(image)

        # Sort image
        if image.mode in ("LA", "RGB", "RGBA"):
            diff = np.abs(datum - datum.mean(axis=(0, 1)))
        else:
            diff = np.abs(datum - datum.mean())

        if diff.mean() <= self.mean_threshold and diff.max() <= self.max_threshold:
            info(f"{self}: '{infile}' matches 'solid'")
            return "solid"
        else:
            info(f"{self}: '{infile}' matches 'not_solid'")
            return "not_solid"

    @property
    def outlets(self) -> List[str]:
        return ["not_solid", "solid"]
