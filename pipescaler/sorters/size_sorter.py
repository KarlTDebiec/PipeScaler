#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Sorts image based on canvas size."""
from __future__ import annotations

from logging import info
from typing import Any

from PIL import Image

from pipescaler.common import validate_int
from pipescaler.core.stages import Sorter


class SizeSorter(Sorter):
    """Sorts image based on canvas size."""

    def __init__(self, cutoff: int = 32, **kwargs: Any) -> None:
        """
        Validate and store static configuration

        Arguments:
            cutoff: Sort as 'less_than' if smallest dimension is below threshold
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store configuration
        self.cutoff = validate_int(cutoff, min_value=1)

    def __call__(self, infile: str) -> str:
        """
        Sort image based on canvas size

        Arguments:
            infile: Input image

        Returns:
            Outlet
        """
        # Read image
        image = Image.open(infile)

        if image.size[0] < self.cutoff or image.size[1] < self.cutoff:
            info(f"{self}: {infile}'s smallest dimension is less than{self.cutoff}")
            return "less_than"
        info(
            f"{self}: {infile}'s smallest dimension is greater than or equal to"
            f" {self.cutoff}"
        )
        return "greater_than_or_equal_to"

    @classmethod
    @property
    def outlets(self):
        """Outlets that flow out of stage"""
        return ["less_than", "greater_than_or_equal_to"]
