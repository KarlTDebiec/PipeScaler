#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Sorts image based on canvas size."""

from __future__ import annotations

from logging import info

from pipescaler.common.validation import val_int
from pipescaler.core.pipelines import Sorter
from pipescaler.image.core.pipelines import PipeImage


class SizeSorter(Sorter):
    """Sorts image based on canvas size."""

    def __init__(self, cutoff: int = 32):
        """Validate configuration and initialize.

        Arguments:
            cutoff: Sort as 'less_than' if image's smallest dimension is less than this;
              otherwise, sort as 'greater_than_or_equal_to'
        """
        self.cutoff = val_int(cutoff, min_value=1)

    def __call__(self, obj: PipeImage) -> str | None:
        """Get the outlet to which an image should be sorted.

        Arguments:
            obj: Image to sort
        Returns:
            Outlet to which image should be sorted
        """
        image = obj.image

        if image.size[0] < self.cutoff or image.size[1] < self.cutoff:
            outlet = "less_than"
        else:
            outlet = "greater_than_or_equal_to"

        info(f"{self}: '{obj.location_name}' matches '{outlet}'")
        return outlet

    def __repr__(self) -> str:
        """Representation."""
        return f"{self.__class__.__name__}(cutoff={self.cutoff!r})"

    @property
    def outlets(self) -> tuple[str, ...]:
        """Outlets to which images may be sorted."""
        return "less_than", "greater_than_or_equal_to"
