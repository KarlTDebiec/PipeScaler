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
from pipescaler.core import PipeImage
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
        image = pipe_image.image

        if image.mode in ("LA", "RGBA"):
            alpha_array = np.array(image)[:, :, -1]
            if alpha_array.min() >= self.threshold:
                info(f"{self}: '{pipe_image.name}' matches 'drop_alpha'")
                return "drop_alpha"
            info(f"{self}: '{pipe_image.name}' matches 'keep_alpha'")
            return "keep_alpha"
        info(f"{self}: {pipe_image.name}' matches 'no_alpha'")
        return "no_alpha"

    def __repr__(self):
        return "<AlphaSorter>"

    @classmethod
    @property
    def outlets(self) -> tuple[str, ...]:
        """Outlets that flow out of stage."""
        return ("drop_alpha", "keep_alpha", "no_alpha")
