#!/usr/bin/env python
#  Copyright (C) 2020-2022. Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Splits a normal map image into separate x, y, and z images."""
from __future__ import annotations

import numpy as np
from PIL import Image

from pipescaler.core.image import Splitter
from pipescaler.core.validation import validate_image


class NormalSplitter(Splitter):
    """Splits a normal map image into separate x, y, and z images."""

    def __call__(self, input_image: Image.Image) -> tuple[Image.Image, ...]:
        """Split an image.

        Arguments:
            input_image: Input image
        Returns:
            Split output images
        """
        input_image = validate_image(input_image, self.inputs["input"])
        input_array = np.array(input_image)
        x_array = input_array[:, :, 0]
        y_array = input_array[:, :, 1]
        z_array = (input_array[:, :, 2].astype(float) - 128) * 2
        z_array = np.clip(z_array, 0, 255).astype(np.uint8)

        x_image = Image.fromarray(x_array)
        y_image = Image.fromarray(y_array)
        z_image = Image.fromarray(z_array)

        return x_image, y_image, z_image

    @classmethod
    @property
    def inputs(cls) -> dict[str, tuple[str, ...]]:
        """Inputs to this operator."""
        return {
            "input": ("RGB",),
        }

    @classmethod
    @property
    def outputs(cls) -> dict[str, tuple[str, ...]]:
        """Outputs of this operator."""
        return {
            "x": ("L",),
            "y": ("L",),
            "z": ("L",),
        }
