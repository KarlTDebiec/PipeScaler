#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Sets entire image color to its average color, optionally resizing."""
from __future__ import annotations

from typing import Any

import numpy as np
from PIL import Image

from pipescaler.common import validate_float
from pipescaler.core.stages.processors import ImageProcessor


class SolidColorProcessor(ImageProcessor):
    """Sets entire image color to its average color, optionally resizing."""

    def __init__(self, scale: float = 1, **kwargs: Any) -> None:
        """
        Validate and store static configuration

        Arguments:
            scale: Factor by which to scale output image relative to input
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store configuration
        self.scale = validate_float(scale)

    def process(self, input_image: Image.Image) -> Image.Image:
        """
        Process an image

        Arguments:
            input_image: Input image to process
        Returns:
            Processed output image
        """
        # noinspection PyTypeChecker
        input_datum = np.array(input_image)

        size = (
            round(input_image.size[0] * self.scale),
            round(input_image.size[1] * self.scale),
        )
        if input_image.mode in ("RGBA", "RGB", "LA"):
            color = tuple(np.rint(input_datum.mean(axis=(0, 1))).astype(np.uint8))
        elif input_image.mode == "L":
            color = round(input_datum.mean())
        else:
            color = 255 if input_datum.mean() >= 0.5 else 0
        # noinspection PyTypeChecker
        output_image = Image.new(input_image.mode, size, color)

        return output_image
