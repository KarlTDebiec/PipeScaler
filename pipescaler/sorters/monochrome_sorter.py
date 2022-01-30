#!/usr/bin/env python
#   pipescaler/sorters/monoochrome_sorter.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Sorts image based on presence and use of colors other than black and white"""
from __future__ import annotations

from logging import info
from typing import Any, List

import numpy as np

from pipescaler.common import validate_float, validate_int
from pipescaler.core import Sorter, validate_image


class MonochromeSorter(Sorter):
    """Sorts image based on presence and use of colors other than black and white"""

    def __init__(
        self, mean_threshold: float = 0, max_threshold: float = 0, **kwargs: Any
    ) -> None:
        """
        Validate and store static configuration

        Arguments:
            mean_threshold: Sort as 'drop_gray' if mean diff is below this threshold
            max_threshold: Sort as 'drop_gray' if maximum diff is below this threshold
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store configuration
        self.mean_threshold = validate_float(mean_threshold, 0, 255)
        self.max_threshold = validate_float(max_threshold, 0, 255)

    def __call__(self, infile: str) -> str:
        """
        Sort image based on presence and use of colors other than black and white

        Arguments:
            infile: Input image

        Returns:
            Outlet
        """
        # Read image
        image = validate_image(infile, ["1", "L"])

        # Sort image
        if image.mode == "L":
            # noinspection PyTypeChecker
            l_array = np.array(image)
            # noinspection PyTypeChecker
            one_array = np.array(image.convert("1").convert("L"))
            diff = np.abs(l_array - one_array)
            if diff.mean() <= self.mean_threshold and diff.max() <= self.max_threshold:
                info(f"{self}: '{infile}' matches 'drop_gray'")
                return "drop_gray"
            else:
                info(f"{self}: '{infile}' matches 'keep_gray'")
                return "keep_gray"
        else:
            info(f"{self}: {infile}' matches 'no_gray'")
            return "no_gray"

    @property
    def outlets(self) -> List[str]:
        """Outlets that flow out of stage"""
        return ["drop_gray", "keep_gray", "no_gray"]
