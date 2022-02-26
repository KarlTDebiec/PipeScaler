#!/usr/bin/env python
#   pipescaler/sorters/alpha_sorter.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Sorts image based on presence and use of alpha channel"""
from __future__ import annotations

from logging import info
from typing import Any, List

import numpy as np

from pipescaler.common import validate_int
from pipescaler.core import Sorter, validate_image


class AlphaSorter(Sorter):
    """Sorts image based on presence and use of alpha channel"""

    def __init__(self, threshold: int = 255, **kwargs: Any) -> None:
        """
        Validate and store static configuration

        Arguments:
            threshold: Sort as 'drop_alpha' if all pixels' alpha is above this threshold
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store configuration
        self.threshold = validate_int(threshold, 0, 255)

    def __call__(self, infile: str) -> str:
        """
        Sort image based on presence and use of alpha channel

        Arguments:
            infile: Input image

        Returns:
            Outlet
        """
        # Read image
        image = validate_image(infile, ["L", "LA", "RGB", "RGBA"])

        # Sort image
        if image.mode in ("LA", "RGBA"):
            # noinspection PyTypeChecker
            alpha_array = np.array(image)[:, :, -1]
            if alpha_array.min() >= self.threshold:
                info(f"{self}: '{infile}' matches 'drop_alpha'")
                return "drop_alpha"
            info(f"{self}: '{infile}' matches 'keep_alpha'")
            return "keep_alpha"
        info(f"{self}: {infile}' matches 'no_alpha'")
        return "no_alpha"

    @property
    def outlets(self) -> List[str]:
        """Outlets that flow out of stage"""
        return ["drop_alpha", "keep_alpha", "no_alpha"]
