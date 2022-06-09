#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Sorts image based on presence and use of alpha channel."""
from __future__ import annotations

from logging import info
from typing import Any

import numpy as np

from pipescaler.common import validate_int
from pipescaler.core import PipeImage, validate_mode
from pipescaler.core.stages import Sorter


class AlphaSorter(Sorter):
    """Sorts image based on presence and use of alpha channel."""

    def __init__(self, threshold: int = 255, **kwargs: Any) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            threshold: Sort as 'drop_alpha' if all pixels' alpha is above this threshold
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store configuration
        self.threshold = validate_int(threshold, 0, 255)

    def __call__(self, pipe_image: PipeImage) -> str:
        outlet = self.sort(pipe_image)
        info(f"{self}: {pipe_image.name} matches '{outlet}'")
        return outlet

    def sort(self, pipe_image: PipeImage) -> str:
        image, mode = validate_mode(pipe_image.image, ("1", "L", "LA", "RGB", "RGBA"))
        if mode in ("LA", "RGBA"):
            alpha_array = np.array(image)[:, :, -1]
            if alpha_array.min() >= self.threshold:
                return "drop_alpha"
            return "keep_alpha"
        return "no_alpha"

    def __repr__(self):
        return "<AlphaSorter>"

    @property
    def outlets(self) -> tuple[str, ...]:
        """Outlets that flow out of sorter."""
        return ("drop_alpha", "keep_alpha", "no_alpha")
