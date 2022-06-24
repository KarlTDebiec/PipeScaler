#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Sorts image based on presence and use of alpha channel."""
from __future__ import annotations

from logging import info

import numpy as np

from pipescaler.common import validate_int
from pipescaler.core.pipelines import PipeImage
from pipescaler.core.pipelines.sorter import Sorter
from pipescaler.core.validation import validate_mode


class AlphaSorter(Sorter):
    """Sorts image based on presence and use of alpha channel."""

    def __init__(self, threshold: int = 255) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            threshold: Sort as 'drop_alpha' if all pixels' alpha is above this threshold
        """
        self.threshold = validate_int(threshold, 0, 255)

    def __call__(self, pipe_image: PipeImage) -> str:
        image, mode = validate_mode(pipe_image.image, ("1", "L", "LA", "RGB", "RGBA"))

        if mode in ("LA", "RGBA"):
            alpha_array = np.array(image)[:, :, -1]
            if alpha_array.min() >= self.threshold:
                outlet = "drop_alpha"
            else:
                outlet = "keep_alpha"
        else:
            outlet = "no_alpha"

        info(f"{self}: {pipe_image.name} matches {outlet}")
        return outlet

    @property
    def outlets(self) -> tuple[str, ...]:
        """Outlets that flow out of sorter."""
        return ("drop_alpha", "keep_alpha", "no_alpha")
