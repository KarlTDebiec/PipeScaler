#!/usr/bin/env python
#   pipescaler/sorters/grayscale_sorter.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Sorts image based on presence and use of color channels"""
from __future__ import annotations

from logging import info
from typing import Any, List

import numpy as np
from PIL import Image

from pipescaler.common import validate_float
from pipescaler.core import Sorter, validate_image


class GrayscaleSorter(Sorter):
    """Sorts image based on presence and use of color channels"""

    def __init__(
            self, mean_threshold: float = 1, max_threshold: float = 10, **kwargs: Any
    ) -> None:
        """
        Validate and store static configuration

        Arguments:
            mean_threshold: Sort as 'drop_rgb' if mean diff is below this threshold
            max_threshold: Sort as 'drop_rgb' if maximum diff is below this threshold
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store configuration
        self.mean_threshold = validate_float(mean_threshold, 0, 255)
        self.max_threshold = validate_float(max_threshold, 0, 255)

    def __call__(self, infile: str) -> str:
        """
        Sort image based on presence and use of color channels

        Arguments:
            infile: Input image

        Returns:
            Outlet
        """
        # Read image
        image = validate_image(infile, ["L", "LA", "RGB", "RGBA"])

        # Sort image
        if image.mode in ("RGB", "RGBA"):
            # noinspection PyTypeChecker
            rgb_array = np.array(image)[:, :, :3]
            l_array = np.array(Image.fromarray(rgb_array).convert("L").convert("RGB"))
            diff = np.abs(rgb_array - l_array)
            if diff.mean() <= self.mean_threshold and diff.max() <= self.max_threshold:
                info(f"{self}: '{infile}' matches 'drop_rgb'")
                return "drop_rgb"
            else:
                info(f"{self}: '{infile}' matches 'keep_rgb'")
                return "keep_rgb"
        else:
            info(f"{self}: {infile}' matches 'no_rgb'")
            return "no_rgb"

    @property
    def outlets(self) -> List[str]:
        """Outlets that flow out of stage"""
        return ["drop_rgb", "keep_rgb", "no_rgb"]
