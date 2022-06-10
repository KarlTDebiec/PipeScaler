#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Sets entire image color to its average color, optionally resizing."""
from __future__ import annotations

import numpy as np
from core import validate_mode
from core.stages import Processor
from PIL import Image

from pipescaler.common import validate_float


class SolidColorProcessor(Processor):
    """Sets entire image color to its average color, optionally resizing."""

    def __init__(self, scale: float = 1) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            scale: Factor by which to scale output image relative to input
            **kwargs: Additional keyword arguments
        """
        self.scale = validate_float(scale)

    def __call__(self, input_image: Image.Image) -> Image.Image:
        input_image, output_mode = validate_mode(input_image, self.inputs["input"])

        size = (
            round(input_image.size[0] * self.scale),
            round(input_image.size[1] * self.scale),
        )
        array = np.array(input_image)
        if input_image.mode in ("LA", "RGB", "RGBA"):
            color = tuple(np.rint(array.mean(axis=(0, 1))).astype(np.uint8))
        elif input_image.mode == "L":
            color = round(array.mean())
        else:
            color = 255 if array.mean() >= 0.5 else 0
        output_image = Image.new(output_mode, size, color)

        return output_image

    @classmethod
    @property
    def inputs(cls) -> dict[str, tuple[str, ...]]:
        return {
            "input": ("1", "L", "LA", "RGB", "RGBA"),
        }

    @classmethod
    @property
    def outputs(cls) -> dict[str, tuple[str, ...]]:
        return {
            "output": ("1", "L", "LA", "RGB", "RGBA"),
        }
