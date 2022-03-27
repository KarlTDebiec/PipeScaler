#!/usr/bin/env python
#   pipescaler/sorters/mode_sorter.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Sorts image based on mode."""
from __future__ import annotations

from logging import info
from typing import List

from pipescaler.core import Sorter, validate_image


class ModeSorter(Sorter):
    """Sorts image based on mode."""

    def __call__(self, infile: str) -> str:
        """
        Sort image based on mode

        Arguments:
            infile: Input image

        Returns:
            Outlet
        """
        # Read image
        image = validate_image(infile, ["1", "L", "LA", "RGB", "RGBA"])

        # Sort image
        info(f"{self}: '{infile}' matches '{image.mode}'")
        return image.mode.lower()

    @classmethod
    @property
    def outlets(self) -> List[str]:
        """Outlets that flow out of stage"""
        return ["rgba", "rgb", "la", "l", "1"]
