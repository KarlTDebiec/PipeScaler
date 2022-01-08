#!/usr/bin/env python
#   pipescaler/sorters/solid_color_sorter.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Sorts image based on presence of multiple colors"""
from __future__ import annotations

from logging import info
from typing import Any, List

import numpy as np

from pipescaler.common import validate_float, validate_int
from pipescaler.core import Sorter, validate_image


class SolidColorSorter(Sorter):
    """Sorts image based on presence of multiple colors"""

    def __init__(
        self, mean_threshold: float = 1, max_threshold: float = 10, **kwargs: Any
    ) -> None:
        """
        Validate and store static configuration

        Arguments:
            mean_threshold: Sort as 'solid' if mean diff is below this threshold
            max_threshold: Sort as 'solid' if maximum diff is below this threshold
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store configuration
        self.mean_threshold = validate_float(mean_threshold, 0, 255)
        self.max_threshold = validate_int(max_threshold, 0, 255)

    def __call__(self, infile: str) -> str:
        """
        Sort image based on presence of multiple colors

        Arguments:
            infile: Input image

        Returns:
            Outlet
        """
        # Read image
        image = validate_image(infile, ["L", "LA", "RGB", "RGBA"])
        array = np.array(image)

        # Sort image
        if image.mode in ("LA", "RGB", "RGBA"):
            diff = np.abs(array - array.mean(axis=(0, 1)))
        else:
            diff = np.abs(array - array.mean())

        if diff.mean() <= self.mean_threshold and diff.max() <= self.max_threshold:
            info(f"{self}: '{infile}' matches 'solid'")
            return "solid"
        else:
            info(f"{self}: '{infile}' matches 'not_solid'")
            return "not_solid"

    @property
    def outlets(self) -> List[str]:
        """Outlets that flow out of stage"""
        return ["not_solid", "solid"]
